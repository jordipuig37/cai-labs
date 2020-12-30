library(igraph)
# Erdos-Renyi model
eps <- 0.3
avg <- c()
N.plot <- c()

# Execute to add more points
N <- 10^seq(2,3.9,0.1)
for (n in N){
  p <- (1+eps) / sqrt(n)
  er <- erdos.renyi.game(n, p)
  if (count_components(er) == 1){
    avg <- c(avg, average.path.length(er))
    N.plot <- c(N.plot, n)
  }
}

# Plot results
lo <- lm(avg~log(N.plot))
plot(N.plot, predict(lo), col='#cb3700', lwd=2, type="l", xlab='Num Nodes', 
     ylab='Average Shortest Path')
points(N.plot, avg, type="b")

