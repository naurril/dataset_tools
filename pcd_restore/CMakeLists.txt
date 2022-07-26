cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

project(pcd_restore)

find_package(PCL 1.9 REQUIRED)

include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})


add_executable (pcd_restore pcd_restore.cpp)
add_executable (pcd_count pcd_count.cpp)
add_executable (pcd_remove0 pcd_remove0.cpp)

target_link_libraries (pcd_restore ${PCL_LIBRARIES})
target_link_libraries (pcd_count ${PCL_LIBRARIES})
target_link_libraries (pcd_remove0 ${PCL_LIBRARIES})
