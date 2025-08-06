class AdjacencyList:
    def __init__(self):
        self.weightedGraph = {}

    def PopulateGraph(self, node, neighbours, blockNumber, neighbourNumbers):
        adjacentVertices = {}

        for x in range(0, len(neighbours)):
            adjacentVertices.update({neighbourNumbers[x] : self.CalculateWeight(node, neighbours[x])})
            
        listRow = {blockNumber : adjacentVertices}
        self.weightedGraph.update(listRow)

    def CalculateWeight(self, startNode, endNode):
        # connections are only horizontal or vertical - never diagonal
        distance = -1

        if startNode.originalLocationX == endNode.originalLocationX: # vertically aligned
            distance = abs(startNode.originalLocationY - endNode.originalLocationY)
        else: # horizontally aligned
            distance = abs(startNode.originalLocationX - endNode.originalLocationX)

        return (distance - 160) / 160 # distance caluclated from left most of each block, instead of the gap between blocks (subtract 160 to account for this - doesnt affect functionality)
                                      # divide by 160 to return a smaller number, distances are always multiples of 160