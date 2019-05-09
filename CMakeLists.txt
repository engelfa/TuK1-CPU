cmake_minimum_required(VERSION 3.13.1)
SET(CMAKE_C_COMPILER gcc-8)
SET(CMAKE_CXX_COMPILER g++-8)
SET(CMAKE_CXX_COMPILER_LAUNCHER ccache)
SET(CMAKE_BUILD_TYPE Release)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic -std=c++17")

project (tuk_cpu)

SET(SOURCES
		src/main.cpp
		#src/Scan.h
		#src/HitStrategy.h
)

add_executable(tuk_cpu ${SOURCES})