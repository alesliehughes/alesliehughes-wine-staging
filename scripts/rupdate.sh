#!/usr/bin/bash

cd ~/source/wine-staging
git fetch
git rebase origin

cd ~/wine-staging/wine
git am --abort
git rebase --abort
git reset --hard origin
git fetch
git rebase origin || exit

cd ~/wine-staging/wine

~/source/wine-staging/patches/myapply.sh || exit

PATCH_DIRS=(
    "combase-silence"
    "d3d11-CheckFeatureSupport"
    "dxgi_IDXGISwapChain4_silence"
    "fltmgr_scanner_example"
    "fltmgr-stubs2"
    "include-winnt"
    "inetcomm-MessageSupport"
#    "inkobj_InkRecognizerContext"  # Currently no patches just definition file.
    "gdiplus_headers"
    "kernel32-GetBinaryType"
    "mfps_new_dll"
    "msado15_command_exec"
    "msado15_error_checks"
    "msisip_MsiSIPVerifyIndirectData"
    "ntdll-NtExtendSection"
    "ntdll-NtQuerySystemInformation"
    "ntdll-NtQuerySystemInformationEx-debugger"
    "ntoskrnl.exe-IoGetDeviceObjectPointer"
    "odbccp2-admin-dialog"
    "ole32-CoGetCallerTID"
#    "oledb32-PromptNew"   # Rebase required.
    "propsys_marshall"
    "rpcrt4_bump_version"
    "rpcrt4-NdrAsyncClientCall2"
    "uiribbon_various"
    "various-movie_maker"
    "various-photoshop"
#    "xgameruntime-support" Rebase required.
    "various_code_audit"
    "various_code_coverity"
    "wintrust_SoftpubAuthenticode"
)

BASE_PATH="$HOME/source/alesliehughes-wine-staging/patches"

# Loop through and apply patches
for dir in "${PATCH_DIRS[@]}"; do
    git am "$BASE_PATH/$dir"/0* || exit 1
done

cd ~/wine-staging
./buildwine.sh
