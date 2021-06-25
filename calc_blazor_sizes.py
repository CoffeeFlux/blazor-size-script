import os, glob, math

# Paths

base_dir = '/Users/ryan/temp/blazor-size-tests/'
path_to_framework = 'bin/release/{0}.0/publish/wwwroot/_framework'

# Add to these for new preview

releases = ['net5', 'net6-p1', 'net6-p2', 'net6-p3', 'net6-p4', 'net6-p5', 'net6-p6']
net6_prev = 'net6-p5'
net6_cur = 'net6-p6'
releases_full = []
for release in releases:
	releases_full.append(release + '-min')
	releases_full.append(release + '-full')

dotnet_js_mapping = {
	'net5-min': 'dotnet.5.0.2.js',
	'net5-full': 'dotnet.5.0.2.js',
	'net6-p1-min': 'dotnet.6.0.0-preview.2.21105.12.js',
	'net6-p1-full': 'dotnet.6.0.0-preview.2.21077.2.js',
	'net6-p2-min': 'dotnet.6.0.0-preview.2.21117.5.js',
	'net6-p2-full': 'dotnet.6.0.0-preview.2.21117.5.js',
	'net6-p3-min': 'dotnet.6.0.0-preview.3.21167.1.js',
	'net6-p3-full': 'dotnet.6.0.0-preview.3.21167.1.js',
	'net6-p4-min': 'dotnet.6.0.0-preview.4.21222.3.js',
	'net6-p4-full': 'dotnet.6.0.0-preview.4.21222.3.js',
	'net6-p5-min': 'dotnet.6.0.0-preview.5.21301.5.js',
	'net6-p5-full': 'dotnet.6.0.0-preview.5.21301.5.js',
	'net6-p6-min': 'dotnet.6.0.0-preview.6.21324.10.js',
	'net6-p6-full': 'dotnet.6.0.0-preview.6.21324.10.js'
}

#
changes = [
	'\n# Notable changes:',
	'\n## net5 to net6-p5:',
	[['net5-min', 'net6-p5-min'], 'br'],
	[['net5-full', 'net6-p5-full'], 'br'],
	[['net5-min', 'net6-p5-min'], 'br', 'dotnet.wasm'],
	[['net5-full', 'net6-p5-full'], 'br', 'dotnet.wasm'],
	[['net5-min', 'net6-p5-min'], 'br', 'System.Private.CoreLib.dll'],
	[['net5-full', 'net6-p5-full'], 'br', 'System.Private.CoreLib.dll'],
	'\n## net6-p4 to net6-p5:',
	[['net6-p4-min', 'net6-p5-min'], 'br'],
	[['net6-p4-full', 'net6-p5-full'], 'br'],
	[['net6-p4-min', 'net6-p5-min'], 'br', 'dotnet.wasm'],
	[['net6-p4-full', 'net6-p5-full'], 'br', 'dotnet.wasm'],
	[['net6-p4-min', 'net6-p5-min'], 'br', 'System.Private.CoreLib.dll'],
	[['net6-p4-full', 'net6-p5-full'], 'br', 'System.Private.CoreLib.dll'],
]

# Fixes mappings

interesting_files = ['dotnet.wasm', 'System.Private.CoreLib.dll', 'System.Text.Json.dll', 'System.Net.Http.dll', 'dotnet.js', 'Microsoft.AspNetCore.Components.dll']
interesting_files_icu = ['dotnet.timezones.blat', 'icudt.dat', 'icudt_CJK.dat', 'icudt_EFIGS.dat', 'icudt_no_CJK.dat']
interesting_files_full = interesting_files + interesting_files_icu
unused_icu_files = ['icudt.dat', 'icudt_CJK.dat', 'icudat_no_CJK.dat']
unused_runtime_files = ['corebindings.c', 'driver.c', 'emcc-flags.txt', 'emcc-version.txt', 'pinvoke-table.h', 'pinvoke.c', 'pinvoke.h', 'dotnet_support.js', 'library_mono.js']
blacklisted_files = unused_icu_files + unused_runtime_files

extensions = {
	'br': '*.br',
	'gz': '*.gz',
	'uc': '*[!(*.br|*.gz)]'
}

bytes_in_kb = 1000

data = {}
total_size_str = ''

# Functions

def round_sig(x, sig=2):
	return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)

def get_sizes_for_ext(config, extension):
	major_release = config[:4]
	publish_dir = os.path.join(base_dir, config, path_to_framework.format(major_release))
	files = glob.glob(os.path.join(publish_dir, extension))
	data = {}
	for file in files:
		basename = os.path.basename(file)
		data[basename] = round_sig(os.path.getsize(file) / bytes_in_kb, 3)
	return data

def sum_sizes(data):
	total_size = 0
	for name, size in data.items():
		skip = False
		for file in blacklisted_files:
			if name.startswith(file):
				skip = True
				break
		if not skip:
			total_size += size
	return round_sig(total_size / bytes_in_kb, 3)

def relative_diff(old, new):
	if old == new:
		return 0
	rel = (new - old) / old
	return str(round_sig(rel * 100))

def add_extension(name, ext):
	if ext != 'uc':
		name += '.' + ext
	return name

def get_sizes(config):
	data = {}
	local_size_str = ''
	for name, extension in extensions.items():
		data[name] = get_sizes_for_ext(config, extension)
		local_size_str += '\t{0}: {1} MB\n'.format(name, str(sum_sizes(data[name])))
		for filename in interesting_files:
			if filename == 'dotnet.js':
				filename = dotnet_js_mapping[config]
			filename = add_extension(filename, name)
			local_size_str += '\t\t{0}: {1} KB\n'.format(filename, data[name][filename])
	return data, local_size_str

def print_chart_for_config(config_type, use_icu):
	line1 = '| File |'
	for release in releases:
		line1 += ' {0} |'.format(release)
	line1 += ' net5 to net6 | net6 preview diff |'
	print(line1)

	print('| --- |' + (' --- |' * (len(releases) + 2)))

	line3 = '| Full |'
	net5_size = 0
	net6_prev_size = 0
	net6_cur_size = 0
	for release in releases:
		release_full = release + config_type
		files_sum = sum_sizes(data[release_full]['br'])
		line3 += ' {0} MB |'.format(files_sum)
		if release == 'net5':
			net5_size = files_sum
		elif release == net6_prev:
			net6_prev_size = files_sum
		elif release == net6_cur:
			net6_cur_size = files_sum
	line3 += ' {0}% |'.format(relative_diff(net5_size, net6_cur_size))
	line3 += ' {0}% |'.format(relative_diff(net6_prev_size, net6_cur_size))
	print(line3)

	files_to_check = interesting_files
	if use_icu:
		files_to_check = interesting_files_full
	for filename in files_to_check:
		line = '| {0} |'.format(filename)
		net5_size = 0
		net6_prev_size = 0
		net6_cur_size = 0
		for release in releases:
			release_full = release + config_type
			filename_full = filename + '.br'
			if filename == 'dotnet.js':
				filename_full = dotnet_js_mapping[release_full] + '.br'
			file_size = data[release_full]['br'][filename_full]
			line += ' {0} KB |'.format(file_size)
			if release == 'net5':
				net5_size = file_size
			elif release == net6_prev:
				net6_prev_size = file_size
			elif release == net6_cur:
				net6_cur_size = file_size
		line += ' {0}% |'.format(relative_diff(net5_size, net6_cur_size))
		line += ' {0}% |'.format(relative_diff(net6_prev_size, net6_cur_size))
		print(line)

# Logic

for release in releases_full:
	total_size_str += '```\n' + release + '\n' 
	data[release], local_size_str = get_sizes(release)
	total_size_str += local_size_str + '```\n'

print('# Size chart:')

print('\n## Min config:\n')
print_chart_for_config('-min', False)

print('\n## Full config:\n')
print_chart_for_config('-full', True)

for comparison in changes:
	if isinstance(comparison, str):
		print(comparison)
	else:
		r1 = comparison[0][0]
		r2 = comparison[0][1]
		ext = comparison[1]
		if len(comparison) == 2:
			sum1 = sum_sizes(data[r1][ext])
			sum2 = sum_sizes(data[r2][ext])
			percent_diff = relative_diff(sum1, sum2)
			print('* {0} to {1} {2}: {3}%'.format(r1, r2, ext, percent_diff))
		else:
			filename = add_extension(comparison[2], ext)
			num1 = data[r1][ext][filename]
			num2 = data[r2][ext][filename]
			percent_diff = relative_diff(num1, num2)
			print('* {0} to {1} {2} {3}: {4}%'.format(r1, r2, ext, comparison[2], percent_diff))

print('\n# Total sizes:\n')
print(total_size_str)
