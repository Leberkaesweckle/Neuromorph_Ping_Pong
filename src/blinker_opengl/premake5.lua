workspace "OpenGLWorkspace"
   configurations { "Debug", "Release" }

project "OpenGLBlinker"
   kind "ConsoleApp"
   language "C++"
   targetdir "bin/%{cfg.buildcfg}"

   files { "**.h", "**.cpp" }

   filter "configurations:Debug"
      defines { "DEBUG" }
      symbols "On"

   filter "configurations:Release"
      defines { "NDEBUG" }
      optimize "On"

   includedirs { "/usr/include" }
   libdirs { "/usr/lib" }
   links { "GL", "glfw", "GLEW" }
