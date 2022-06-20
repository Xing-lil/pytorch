load("//tools/build_defs:glob_defs.bzl", "subdir_glob")

# kineto code should be updated to not have to
# suppress these warnings.
KINETO_COMPILER_FLAGS = [
    "-fexceptions",
    "-Wno-deprecated-declarations",
    "-Wno-unused-function",
    "-Wno-unused-private-field",
]

def define_kineto():
    cxx_library(
        name = "libkineto",
        srcs = [
            "kineto/src/ActivityProfilerController.cpp",
            "kineto/src/ActivityProfilerProxy.cpp",
            "kineto/src/CuptiActivityApi.cpp",
            "kineto/src/CuptiActivityProfiler.cpp",
            "kineto/src/CuptiRangeProfilerApi.cpp",
            "kineto/src/Demangle.cpp",
            "kineto/src/init.cpp",
            "kineto/src/output_csv.cpp",
            "kineto/src/output_json.cpp",
        ],
        headers = subdir_glob(
            [
                ("kineto/include", "*.h"),
                ("kineto/src", "*.h"),
            ],
        ),
        compiler_flags = KINETO_COMPILER_FLAGS,
        link_whole = True,
        visibility = ["PUBLIC"],
        exported_deps = [
            ":base_logger",
            ":libkineto_api",
            ":thread_util",
            ":fmt",
        ],
    )

    cxx_library(
        name = "libkineto_api",
        srcs = [
            "kineto/src/libkineto_api.cpp",
        ],
        headers = subdir_glob(
            [
                ("kineto/include", "*.h"),
                ("kineto/src", "*.h"),
            ],
        ),
        compiler_flags = KINETO_COMPILER_FLAGS,
        link_whole = True,
        visibility = ["PUBLIC"],
        exported_deps = [
            ":base_logger",
            ":config_loader",
            ":thread_util",
            ":fmt",
        ],
    )

    cxx_library(
        name = "config_loader",
        srcs = [
            "kineto/src/ConfigLoader.cpp",
        ],
        headers = subdir_glob(
            [
                ("kineto/include", "ActivityType.h"),
                ("kineto/src", "*.h"),
            ],
        ),
        compiler_flags = KINETO_COMPILER_FLAGS,
        exported_deps = [
            ":config",
            ":thread_util",
        ],
    )

    cxx_library(
        name = "config",
        srcs = [
            "kineto/src/AbstractConfig.cpp",
            "kineto/src/ActivityType.cpp",
            "kineto/src/Config.cpp",
        ],
        compiler_flags = KINETO_COMPILER_FLAGS,
        public_include_directories = [
            "kineto/include",
            "kineto/src",
        ],
        raw_headers = glob([
            "kineto/include/*.h",
            "kineto/src/*.h",
        ]),
        exported_deps = [
            ":logger",
            ":thread_util",
            ":fmt",
        ],
    )

    cxx_library(
        name = "logger",
        srcs = [
            "kineto/src/ILoggerObserver.cpp",
            "kineto/src/Logger.cpp",
        ],
        compiler_flags = KINETO_COMPILER_FLAGS,
        public_include_directories = [
            "kineto/include",
            "kineto/src",
        ],
        raw_headers = [
            "kineto/include/ILoggerObserver.h",
            "kineto/include/ThreadUtil.h",
            "kineto/src/Logger.h",
            "kineto/src/LoggerCollector.h",
        ],
        exported_deps = [
            ":thread_util",
            ":fmt",
        ],
    )

    cxx_library(
        name = "base_logger",
        srcs = [
            "kineto/src/GenericTraceActivity.cpp",
        ],
        public_include_directories = [
            "kineto/include",
            "kineto/src",
        ],
        raw_headers = glob([
            "kineto/include/*.h",
            "kineto/src/*.h",
            "kineto/src/*.tpp",
        ]),
        exported_deps = [
            ":thread_util",
        ],
    )

    cxx_library(
        name = "thread_util",
        srcs = [
            "kineto/src/ThreadUtil.cpp",
        ],
        compiler_flags = KINETO_COMPILER_FLAGS,
        exported_preprocessor_flags = [
            "-DKINETO_NAMESPACE=libkineto",
        ],
        public_include_directories = [
            "kineto/include",
        ],
        raw_headers = [
            "kineto/include/ThreadUtil.h",
        ],
        exported_deps = [
            ":fmt",
        ],
    )
