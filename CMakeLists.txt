cmake_minimum_required(VERSION 3.5.1)

SET(PROJECT_NAME tuk_cpu)
project(${PROJECT_NAME})

# ON or OFF
SET(USE_PAPI $ENV{PAPI})

SET(CMAKE_BUILD_TYPE Debug)
SET(CMAKE_C_COMPILER gcc)
SET(CMAKE_CXX_COMPILER g++)
SET(CMAKE_CXX_COMPILER_LAUNCHER ccache)
SET(CMAKE_BUILD_TYPE Release)
SET(CMAKE_CXX_STANDARD 17)
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -Wall -Wextra -Wpedantic -std=c++17 -Wno-sign-compare -Wno-unused-parameter")

# Add PAPI via separate cmake file
# set(CMAKE_MODULE_PATH "${CMAKE_MODULE_PATH};${CMAKE_CURRENT_SOURCE_DIR}/cmake")

# if(${USE_PAPI})
# 	find_package(PAPI REQUIRED)
# 	include_directories(${PAPI_INCLUDE_DIRS})
# endif()

SET(SOURCES
		src/main.cpp
		src/Scan.h
		src/ScanConfig.h
		src/BenchmarkConfig.h
)

add_executable(${PROJECT_NAME} ${SOURCES})
target_link_libraries(${PROJECT_NAME} papi)
# if(${USE_PAPI})
# 	target_link_libraries(${PROJECT_NAME} ${PAPI_LIBRARIES})
# endif()
