FROM ubuntu:14.04
MAINTAINER Dany Vohl <vohl@astron.nl>

# Install all necessary system packages
WORKDIR /
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get -y --force-yes install x-window-system
RUN apt-get install -y csh tcsh
RUN apt-get install -y freeglut3
RUN apt-get install -y freeglut3-dev
RUN apt-get install -y libfreetype6 libfreetype6-dev
RUN apt-get install -y binutils-gold
RUN apt-get install -y g++ cmake
RUN apt-get install -y libglew-dev
RUN apt-get install -y git 
RUN apt-get install -y mesa-utils libgl1-mesa-glx mesa-common-dev
RUN apt-get install -y build-essential
RUN apt-get install -y libglew1.5-dev libglm-dev libpng-dev vim
RUN apt-get install -y libhpdf-2.2.1 libhpdf-dev

# RUN apt-get -qq -y update && apt-get -qq -y install sudo \
#     build-essential \
#     apt-utils \
#     git \
#     g++ \
#     csh tcsh \
#     mesa
#     freeglut3 freeglut3-dev \
#     libfreetype6 libfreetype6-dev libgd2-xpm-dev xorg openbox \
#     libpng-dev

#libhpdf-2.2.1 libhpdf-dev

RUN apt-get clean

# Clone S2PLOT
WORKDIR /usr/local/
RUN git clone https://github.com/mivp/s2plot.git

# Install S2PLOT
ENV S2PATH="/usr/local/s2plot"
ENV S2ARCH="linux-gnu-x86_64"
ENV S2FREEGLUT="yes"
ENV S2FREETYPE="yes"
ENV S2INSTALLPATH=${S2PATH}/bin
ENV S2PLOT_PRCDRIVER="s2prcwriter"
# ENV S2PLOT_WIDTH="1000"
# ENV S2PLOT_HEIGHT="820"
ENV S2SHARED="no"
ENV S2PLOT_PRCDRIVER='s2prcwriter'
# ENV S2MPI='yes'
ENV S2MPI=no
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:${S2PATH}/${S2ARCH}
ENV PATH=$PATH:${S2PATH}/scripts:${S2PATH}/${S2ARCH}

WORKDIR /usr/local/s2plot
# RUN locate X11
RUN sed -i 's/S2X11PATH=\/usr\/X11R6/S2X11PATH=\/usr\/bin\/X11/g' scripts/s2plot.csh
RUN sed -i 's/\-lm/\-ldl \-lm/g' scripts/build-examples.csh
RUN /bin/csh -c ./scripts/build.csh
