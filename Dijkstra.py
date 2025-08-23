import Setup

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

class PriorityQueue:
    def __init__(self):
        self.queue = []

    def PeekHighestPriority(self):
        return self.queue[0]

    def IsEmpty(self):
        if len(self.queue) == 0:
            return True

        return False

    def Enqueue(self, value, priority): # a smaller number is a higher priority than a large number
        itemToAdd = (value, priority)
    
        if not self.IsEmpty():
            for itemIndex in range(0, len(self.queue)):
                if itemIndex[1] > priority:
                    self.queue.insert(itemIndex, itemToAdd)
        else:
            self.queue.append(itemToAdd)

    def Dequeue(self): 
        return self.queue.pop(0)

class Dijkstra:
    def __init__(self, graph):
        self.graph = graph
        self.priorityQueue = PriorityQueue()
        self.unvisitedNodes = []
        self.tentativeDistances = {}

    def PopulateInitialListsDicts(self, startNode):
        for node in self.graph:
            self.unvisitedNodes.append(node)

            if node == startNode:
                self.tentativeDistances.update({node : 0})
            else:
                self.tentativeDistances.update({node : Setup.sys.maxsize})

    def UpdateQueue(self, currentNode):
        neighbours = self.graph[currentNode] # stored in format {{neighbour : distance}, {neighbour2 : distance2}}

        for neighbourNode, neighbourNodeDistance in neighbours.items():
            tentative = self.tentativeDistances[currentNode] + neighbourNodeDistance

            if tentative < self.tentativeDistances[neighbourNode]:
                self.tentativeDistances[neighbourNode] = tentative
                self.priorityQueue.Enqueue(neighbourNode, tentative)

    def PerformAlgorithm(self, startNode):
        self.PopulateInitialListsDicts(startNode)

        while not self.priorityQueue.IsEmpty():
            currentNode = self.priorityQueue.Dequeue()[0]

            if currentNode in self.unvisitedNodes:
                self.UpdateQueue(currentNode)
                self.unvisitedNodes.remove(currentNode)
