library(igraph)
# Reference point
n <- 1000
ws_graph <- watts.strogatz.game(1, n, 4, 0)
cc0 <- transitivity(ws_graph)
avg.shortest.path0 <- average.path.length(ws_graph)

# Logarithmic range for p
P <- 10 ^ seq(-4,0,0.2)

# WS model
ccoef <- c()
avg.shortest.path <- c()
for (p in P){
  ws_graph <- watts.strogatz.game(1, n, 4, p)
  # Clustering coefficient
  ccoef <- c(ccoef, transitivity(ws_graph) / cc0)
  # Average shortest path
  avg.shortest.path <- c(avg.shortest.path, average.path.length(ws_graph) / avg.shortest.path0)
}

# Logarithmic tick on axis
log10Tck <- function(side, type){
  lim <- switch(side, 
                x = par('usr')[1:2],
                y = par('usr')[3:4],
                stop("side argument must be 'x' or 'y'"))
  at <- -4: 0
  return(switch(type, 
                minor = outer(1:9, 10^(min(at):(max(at)-1))),
                major = 10^at,
                stop("type argument must be 'major' or 'minor'")
  ))
}

# Plot both variables
options(scipen=5)
plot(P, avg.shortest.path,pch=1, ylab='coeff', log='x', ylim=c(0,1), axes=F)
points(P, ccoef, pch=15, ylab='coeff', ylim=c(0,1))
axis(1, at=log10Tck('x','major'), tcl= 0.2) # bottom
axis(3, at=log10Tck('x','major'), tcl= 0.2, labels=NA) # top
axis(1, at=log10Tck('x','minor'), tcl= 0.1, labels=NA) # bottom
axis(3, at=log10Tck('x','minor'), tcl= 0.1, labels=NA) # top
axis(2) # normal y axis
axis(4, labels=NA) # normal y axis on right side of plot
box()
legend("topright", legend=c("Average Shortest Path", "Clustering Coefficient"),
      pch=c(1,15), cex=0.8)
