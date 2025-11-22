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

    def FinaliseGraph(self, allNodes): # some connections are directed so fill empty connections
        for node in allNodes:
            if node not in self.weightedGraph:
                self.weightedGraph[node] = {}

class PriorityQueue:
    def __init__(self):
        self.queue = []

    def PeekHighestPriority(self):
        if self.IsEmpty():
            raise IndexError("Queue is empty (peek)")

        return self.queue[0]

    def IsEmpty(self):
        if len(self.queue) == 0:
            return True

        return False

    def Enqueue(self, value, priority): # a smaller number is a higher priority than a large number
        itemToAdd = (value, priority)
    
        if self.IsEmpty():
            self.queue.append(itemToAdd)
            return

        inserted = False

        for itemIndex in range(0, len(self.queue)):
            if priority < self.queue[itemIndex][1]:
                self.queue.insert(itemIndex, itemToAdd)
                inserted = True
                break

        if not inserted:
            self.queue.append(itemToAdd)
          
    def Dequeue(self): 
        if self.IsEmpty():
            raise IndexError("Queue is empty (dequeue)")
            
        return self.queue.pop(0)

class DijkstraImplementation:
    def __init__(self, graph):
        self.graph = graph
        self.priorityQueue = PriorityQueue()
        self.unvisitedNodes = set()
        self.tentativeDistances = {}
        self.predecessors = {} # used to be able to recall the shortest path

    def PopulateInitialListsDicts(self, startNode):
        for node in self.graph:
            self.unvisitedNodes.add(node)
            self.predecessors.update({node : None})

            if node == startNode:
                self.tentativeDistances.update({node : 0})
            else:
                self.tentativeDistances.update({node : Setup.sys.maxsize})

    def UpdateQueue(self, currentNode):
        if currentNode not in self.graph:
            raise KeyError(f"{currentNode} not in graph")
        
        neighbours = self.graph[currentNode]

        if neighbours:
            for neighbourNode, neighbourNodeDistance in neighbours.items():
                tentative = self.tentativeDistances[currentNode] + neighbourNodeDistance

                if neighbourNode not in self.tentativeDistances:
                    raise KeyError(f"{neighbourNode} not in tentativeDistances")
            
                if tentative < self.tentativeDistances[neighbourNode]:
                    self.tentativeDistances[neighbourNode] = tentative
                    self.predecessors[neighbourNode] = currentNode
                    self.priorityQueue.Enqueue(neighbourNode, tentative)

    def PerformAlgorithm(self, startNode, goalNode):
        if not self.graph:
            raise ValueError("Graph is empty")

        if startNode not in self.graph:
            raise ValueError(f"{startNode} not in graph.")

        if goalNode not in self.graph:
            raise ValueError(f"{goalNode} not in graph.")

        self.PopulateInitialListsDicts(startNode)
        self.priorityQueue.Enqueue(startNode, 0)

        while not self.priorityQueue.IsEmpty():
            currentNode = self.priorityQueue.Dequeue()[0]

            if currentNode not in self.unvisitedNodes:
                continue

            if self.tentativeDistances[currentNode] == Setup.sys.maxsize:
                break # if smallest distance is infinite then the remaining nodes are unreachable

            if currentNode == goalNode:
                break

            self.UpdateQueue(currentNode)
            self.unvisitedNodes.remove(currentNode)

    def RecallShortestPath(self, goalNode):
        if self.tentativeDistances.get(goalNode, Setup.sys.maxsize) == Setup.sys.maxsize:
            return None # if there is no path

        shortestPath = []
        current = goalNode

        while current != None:
            shortestPath.insert(0, current)
            current = self.predecessors[current]

        return shortestPath 