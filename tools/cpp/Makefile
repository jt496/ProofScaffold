# C++ toolkit.
#   make          build every program in this directory
#   make clean    remove the binaries
# BINS is derived from the sources, so a new .cpp file is picked up
# automatically; it needs a rule of its own only if it needs extra flags.

CXX      ?= g++
CXXFLAGS ?= -O3 -march=native -std=c++17 -Wall

SRCS := $(wildcard *.cpp)
BINS := $(SRCS:.cpp=)

all: $(BINS)

%: %.cpp core.hpp
	$(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -f $(BINS)

.PHONY: all clean
