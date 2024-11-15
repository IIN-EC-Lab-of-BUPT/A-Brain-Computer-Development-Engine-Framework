
#ifndef _FFCONFIG_H
#define _FFCONFIG_H

#include "SDL_version.h"
#define SDL_VERSIONNUM(X, Y, Z) ((X)*1000 + (Y)*100 + (Z))
#define SDL_VERSION_ATLEAST(X, Y, Z) (SDL_COMPILEDVERSION >= SDL_VERSIONNUM(X, Y, Z))
#if defined(__APPLE__) && SDL_VERSION_ATLEAST(1, 2, 14)
#define MAC_REALLOC 1
#else
#define MAC_REALLOC 0
#endif

#if !defined(_WIN32) && !defined(__APPLE__)
#define NOT_WIN_MAC 1
#else
#define NOT_WIN_MAC 0
#endif

#if defined(_WIN32)
#define WIN_IS_DEFINED 1
#else
#define WIN_IS_DEFINED 0
#endif

#define CONFIG_AVFILTER 1
#define CONFIG_AVDEVICE 1
#define CONFIG_SWSCALE 1
#define CONFIG_RTSP_DEMUXER 1
#define CONFIG_MMSH_PROTOCOL 1
#define CONFIG_POSTPROC 0
#define CONFIG_SDL 1
#define HAS_SDL2 1
#define USE_SDL2_MIXER 1
#define CONFIG_AVUTIL 1
#define CONFIG_AVCODEC 1
#define CONFIG_AVFORMAT 1
#define CONFIG_SWRESAMPLE 1

#endif
