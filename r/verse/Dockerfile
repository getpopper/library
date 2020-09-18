FROM rocker/verse:4.0.0

LABEL maintainer="apoirel@ucsc.edu"
LABEL description="Used as a base for Popper workflows using R and rstudio"
# labels match the corresponding Rocker image
LABEL version="4.0.0"

# move configuration file where rstudio server will find it
COPY rsession.conf /etc/rstudio 

# install containerit
RUN R -e "devtools::install_github(\"o2r-project/containerit\")"
 
EXPOSE 8787
CMD ["bin/sh"] 