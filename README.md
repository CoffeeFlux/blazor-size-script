# Blazor size comparison script

Running it is as easy as `python calc_blazor_sizes.py > preview_sizes.md` — setup is the hard part ;)

I do apologize for how messy this is, but it was never intended for anyone but me to see or use. I promise I write nice code otherwise!

## Setup

You need a base directory to hold all the projects. Set `base_dir` to its location in the script.

Within that directory, you want to generate Blazor projects named like so:

```
ryan@kenshin:~/temp/blazor-size-tests$ ls
net5-full    net5-min     net6-p1-full net6-p1-min  net6-p2-full net6-p2-min  net6-p3-full net6-p3-min  net6-p4-full net6-p4-min  net6-p5-full net6-p5-min  net6-p6-full net6-p6-min
```

Creating a new project is done like so:

```
mkdir net6-p7-full
cd net6-p7-full
dotnet net blazorwasm
dotnet publish -c release
```

For the min config, edit the config file to include:

```
    <BlazorEnableTimeZoneSupport>false</BlazorEnableTimeZoneSupport>
    <InvariantGlobalization>true</InvariantGlobalization>
```

You need to add a full and min as a pair.

Add to `releases` in the script, set `net6_prev` and `net6_cur`, and set the `dotnet_js_mapping` entry for each project. The mapping is terrible but I was too lazy to glob.
