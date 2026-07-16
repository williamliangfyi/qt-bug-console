cmake_minimum_required(VERSION 3.16)
project(ci_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(calc src/calc.cpp)
target_include_directories(calc PUBLIC src)

add_executable(demo src/main.cpp)
target_link_libraries(demo PRIVATE calc)

enable_testing()
add_executable(test_calc tests/test_calc.cpp)
target_link_libraries(test_calc PRIVATE calc)
add_test(NAME test_calc COMMAND test_calc)
