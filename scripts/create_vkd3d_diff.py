#!/usr/bin/env python3

import os, subprocess, shutil, sys
import re

subs = ["vkd3d", "vkd3d-common", "vkd3d-shader", "vkd3d-utils"]
incl = ["include"]
types = (".h", ".c", ".y", ".l")
maketypes = (".c", ".y", ".l")

hlslex = ("vkd3d-shader/fx.c", "vkd3d-shader/hlsl_constant_ops.c", "vkd3d-shader/hlsl.c", "vkd3d-shader/hlsl.l", "vkd3d-shader/hlsl.y",
		"vkd3d-shader/hlsl_codegen.c", "vkd3d-shader/d3dbc.c", "vkd3d-shader/tpf.c",
		"vkd3d-shader/vkd3d_shader_main.c", )

skip_include = ("config.h",
				"appkit.h",
				"foundation.h",
				"list.h",
				"quartzcore.h",
				"rbtree.h",
				"vkd3d_test.h",
				"vkd3d_d3d9types.h",
				"vkd3d_d3d12.h",
				"vkd3d_d3d12sdklayers.h",
				"vkd3d_d3d10shader.h",
				"vkd3d_d3d10_1shader.h",
				"vkd3d_d3d11shader.h",
				"vkd3d_d3d12shader.h",
				"vkd3d_d3dcommon.h",
				"vkd3d_d3dcompiler.h",
				"vkd3d_d3dcompiler_types.h",
				"vkd3d_d3dx9shader.h",
				"vkd3d_dxgi.h",
				"vkd3d_dxgi1_2.h",
				"vkd3d_dxgi1_3.h",
				"vkd3d_dxgi1_4.h",
				"vkd3d_dxgibase.h",
				"vkd3d_dxgiformat.h",
				"vkd3d_dxgitype.h",
				"vkd3d_utils.h",
				"vkd3d_windows.h"
				)

skip_source = (
				#"vkd3d-shader/vkd3d_shader_main.c",
				"vkd3d-shader/hlsl.yy.c",
				"vkd3d-shader/hlsl.tab.c",
				"vkd3d-shader/hlsl.tab.h",
				"vkd3d-shader/preproc.tab.c",
				"vkd3d-shader/preproc.tab.h",
				"vkd3d-shader/preproc.yy.c",
#				"vkd3d-utils/reflection.c" 
				)

vkd3d_base = '/home/alesliehughes/source/vkd3d/'
vkd3d_libs = vkd3d_base + 'libs'

wine_base = '/home/alesliehughes/wine-build/wine/libs/vkd3d/'
winedir = wine_base + 'libs'

filelist = [ ]

def create_vkd3d_makefile():
	filelist.sort()
	filelist.insert(0, "config.h")

	last_item = filelist[-1]
	with open(wine_base + "Makefile.in", 'w') as file:
		file.write('STATICLIB = libvkd3d.a\n')
		file.write('EXTRAINCL = $(VKD3D_PE_CFLAGS) -I$(srcdir)/include/private -I$(srcdir)/libs/vkd3d -I$(srcdir)/libs/vkd3d-shader\n')
		file.write('EXTRADEFS = \\\n')
		file.write('\t-DWINE_NO_NAMELESS_EXTENSION \\\n')
#		file.write('\t-DCONST_VTABLE \\\n')
		file.write('\t-DLIBVKD3D_SOURCE \\\n')
		file.write('\t-DLIBVKD3D_SHADER_SOURCE \\\n')
		file.write('\t-DLIBVKD3D_UTILS_SOURCE\n')
		file.write('\n')
		file.write('SOURCES = \\\n')

		for str in filelist:
			filestr = str.replace(winedir, 'libs')
			file.write("\t" + filestr)
			if str != last_item:
				file.write(" \\\n")
			else:
				file.write("\n")

def replace_single_include(data, header, replacement):
	pattern = rf'^(\s*#\s*include\s*["<]){header}([">])'
	replacement = rf'\g<1>{replacement}\g<2>'


#	print(pattern)
#	print(replacement)
	data = re.sub(pattern, replacement, data, flags=re.MULTILINE)
#	print(updated_code)

#	str = '"' + include +'"'
#	rep = '"' + replacement +'"'
#	data = data.replace(str, rep)

#	str = '<' + include +'>'
#	rep = '<' + replacement +'>'
#	data = data.replace(str, rep)

	return data

def replace_includes(filename):
	filedata = None

	with open(filename, 'r') as file:
		filedata = file.read()

	# Use standard windows headers.
	filedata = replace_single_include(filedata, "vkd3d_windows.h", "windows.h")
	filedata = replace_single_include(filedata, "vkd3d_d3d12.h", "d3d12.h")
	filedata = replace_single_include(filedata, "vulkan/vulkan.h", "wine/vulkan.h")
	filedata = replace_single_include(filedata, "vkd3d_d3dcommon.h", "d3dcommon.h")
	filedata = replace_single_include(filedata, "vkd3d_d3dcompiler.h", "d3dcompiler.h")
	filedata = replace_single_include(filedata, "vkd3d_d3dx9shader.h", "d3dx9shader.h")
#	filedata = replace_single_include(filedata, "vkd3d_d3d10shader.h", "d3d10shader.h")
	filedata = replace_single_include(filedata, "vkd3d_d3d10shader.h", "d3d10effect.h")
	filedata = replace_single_include(filedata, "vkd3d_d3d10_1shader.h", "d3d10_1shader.h")
	filedata = replace_single_include(filedata, "vkd3d_d3d11shader.h", "d3d11shader.h")
	filedata = replace_single_include(filedata, "vkd3d_d3d12shader.h", "d3d12shader.h")

	filedata = filedata.replace('"rbtree.h"', '"wine/rbtree.h"')
	filedata = filedata.replace('"list.h"', '"wine/list.h"')

	if not filename.endswith(hlslex):
		filedata = filedata.replace('"hlsl.h"', '"vkd3d_shader_private.h"')
		filedata = filedata.replace('#include "preproc.tab.h"', '#include "preproc.h"\n#include "preproc.tab.h"')


	# Stops duplication linking of IID_*
	filedata = filedata.replace('#define INITGUID', '')

	# No-op the IMPORT/EXPORT, we are statically linking.
	filedata = filedata.replace('# define VKD3D_IMPORT __declspec(dllimport)', '# define VKD3D_IMPORT')
	filedata = filedata.replace('# define VKD3D_EXPORT __declspec(dllexport)', '# define VKD3D_EXPORT')

	# Stops duplicate of vkd3d_dbg_env_name
	filedata = filedata.replace('VKD3D_DEBUG_ENV_NAME("VKD3D_SHADER_DEBUG");', '/* VKD3D_DEBUG_ENV_NAME("VKD3D_SHADER_DEBUG"); */')

	if filename.endswith("vkd3d_utils_main.c"):
		filedata = filedata.replace('VKD3D_DEBUG_ENV_NAME("VKD3D_DEBUG");', '/* VKD3D_DEBUG_ENV_NAME("VKD3D_DEBUG"); */')

	# Rewrite the file.
	with open(filename, 'w') as file:
		file.write(filedata)

def main():
	rootdir = os.path.join(vkd3d_base, 'include')
	for subdir, dirs, files in os.walk(rootdir):
		for file in files:
			if file.endswith(skip_include):
				continue
			if file.endswith(types):
				target = os.path.join(subdir, file)
				target = target.replace(vkd3d_base, wine_base)
				print("Copying file to: " + target)
				shutil.copyfile(os.path.join(subdir, file), target)
				replace_includes(target)

	for d in subs:
		rootdir = os.path.join(vkd3d_libs, d)
		for subdir, dirs, files in os.walk(rootdir):
			for file in files:
				target = os.path.join(subdir, file)
				if target.endswith(skip_source):
					continue
				if file.endswith(types):
					target = target.replace(vkd3d_base, wine_base)
					print("Copying file to: " + target)

					if file.endswith(maketypes):
						filelist.append(target)
					shutil.copyfile(os.path.join(subdir, file), target)
					replace_includes(target)

	create_vkd3d_makefile()

main()

# Get vkd3d SHA1 of what we are compare to.
xx = subprocess.run(['git','rev-parse','origin/master'], cwd=vkd3d_base, capture_output=True, text=True)
print (xx.stdout)
msg = 'Updated vkd3d to ' + xx.stdout
msg = msg.strip() + '.'
xx = subprocess.run(['git','commit','-a','-m', msg], cwd=wine_base, capture_output=True, text=True)
print (xx.stdout)
