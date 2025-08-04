class AdjacencyList:
    def __init__(self):
        self.graph = []

    def PopulateGraph(self, node, neighbours):
        adjacentVertices = {}

        for neighbour in neighbours:
            adjacentVertices.append([neighbour, self.CalculateWeight(node, neighbour)])
            
        listRow = {node : adjacentVertices}
        self.graph.append(listRow)

    def CalculateWeight(self, startNode, endNode):
        # connections are only horizontal or vertical - never diagonal
        distance = -1

        if startNode.originalLocationX == endNode.originalLocationX: # vertically aligned
            distance = abs(startNode.originalLocationY - endNode.originalLocationY)
        else: # horizontally aligned
            distance = abs(startNode.originalLocationX - endNode.originalLocationX)

        return distance