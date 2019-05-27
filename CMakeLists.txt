cmake_minimum_required(VERSION 3.6.2)
SET(CMAKE_C_COMPILER gcc)
SET(CMAKE_CXX_COMPILER g++)
SET(CMAKE_CXX_COMPILER_LAUNCHER ccache)
SET(CMAKE_BUILD_TYPE Release)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -Wall -Wextra -Wpedantic -std=c++17")

project (tuk_cpu)

SET(SOURCES
		src/main.cpp
		src/Scan.h
		src/ScanConfig.h
)

add_executable(tuk_cpu ${SOURCES})
