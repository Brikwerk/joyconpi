#
# JoyConPi - A JoyCon Emulator for the Raspberry Pi
# Copyright (C) 2019-2020  Reece Walsh <reece@brikwerk.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

cmake_minimum_required(VERSION 3.4)

project(joyconpi)

# Source files include list
# Includes gdbus-codegen files
set(SRC_LIST
    main.c
    ${CMAKE_CURRENT_BINARY_DIR}/org-bluez-adapter1.c
    ${CMAKE_CURRENT_BINARY_DIR}/org-bluez-profilemanager1.c
)

find_package(PkgConfig REQUIRED)

# Show all the warnings
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall")

# Adding dbus library
pkg_check_modules(DBus REQUIRED dbus-1>=1.12.6)
include_directories(${DBUS_INCLUDE_DIRS})
link_directories(${DBUS_LIBRARY_DIRS})

# Adding glib library
pkg_check_modules(GLIB REQUIRED glib-2.0>=2.26 gio-2.0>=2.26)
include_directories(${GLIB_INCLUDE_DIRS})
link_directories(${GLIB_LIBRARY_DIRS})

# Adding glib library
pkg_check_modules(GIOUNIX REQUIRED gio-unix-2.0>=2.26)
include_directories(${GIOUNIX_INCLUDE_DIRS})
link_directories(${GIOUNIX_LIBRARY_DIRS})

# Generating GDBus BlueZ API C files
find_program(GDBUSCODEGEN NAMES gdbus-codegen)
if (NOT GDBUSCODEGEN)
    message(SEND_ERROR "Could not find gdbus-codegen")
endif(NOT GDBUSCODEGEN)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/org-bluez-adapter1.c
    COMMAND ${GDBUSCODEGEN} --generate-c-code=org-bluez-adapter1 ${PROJECT_SOURCE_DIR}/bluez-dbus/org.bluez.Adapter1.xml
    DEPENDS ${PROJECT_SOURCE_DIR}/bluez-dbus/org.bluez.Adapter1.xml
)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/org-bluez-profilemanager1.c
    COMMAND ${GDBUSCODEGEN} --generate-c-code=org-bluez-profilemanager1 ${PROJECT_SOURCE_DIR}/bluez-dbus/org.bluez.ProfileManager1.xml
    DEPENDS ${PROJECT_SOURCE_DIR}/bluez-dbus/org.bluez.ProfileManager1.xml
)

include_directories(${CMAKE_CURRENT_BINARY_DIR})

add_executable("${PROJECT_NAME}" ${SRC_LIST})

target_link_libraries("${PROJECT_NAME}" ${DBUS_LIBRARIES})
target_link_libraries("${PROJECT_NAME}" ${GLIB_LIBRARIES})
target_link_libraries("${PROJECT_NAME}" ${GIOUNIX_LIBRARIES})
