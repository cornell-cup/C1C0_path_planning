import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.PriorityQueue;
import java.util.Set;

public class Search {
	public static void main(String[] args) {
		Node[][] grid = Node.createGrid(5, 5);
		int result = search(grid, grid[0][0], grid[3][4]);
		System.out.println(result);
		Node cur = grid[3][4];
		while(cur != null) {
			System.out.println(cur.x + "," + cur.y);
			cur = cur.parent;
		}
	}


	private static int search(Node[][] grid, Node start, Node end) {
		int r = grid.length;
		int c = grid[0].length;

		Comparator<Node> comparator = new Comparator<Node>() {
			@Override
			public int compare(Node node1, Node node2) {
				return node1.g + node1.h - (node2.g + node2.h);
			}
		};

		PriorityQueue<Node> open = new PriorityQueue<Node>(comparator);

		Set<Node> closed = new HashSet();

		//1
		start.g = 0;
		start.h = heuristic(start, end);
		open.add(start);

		//2
		while(!open.isEmpty()) {
			//A
			Node cur = open.poll();
			//B
			closed.add(cur);
			int x = cur.x;
			int y = cur.y;
			int[] successors = new int[] {x - 1, y, x + 1, y, x, y - 1, x, y + 1};
			List<Node> nextNodes = new LinkedList();
			for(int i = 0; i + 1 < 8; i = i + 2) {
				int xS = successors[i];
				int yS = successors[i + 1];
				if(0 <= xS && xS < r && 0 <= yS && yS < c) {
					Node next = grid[xS][yS];
					//next.parent = cur;
					nextNodes.add(next);
				}
			}
			//C1
			for(Node next : nextNodes) {
				if(next == end) {
					next.parent = cur;
					next.g = cur.g + 1;
					return next.g;
				}
				if(closed.contains(next) || next.object) {
					continue;
				}
				if(!open.contains(next)) {
					open.add(next);
					next.parent = cur;
					next.g = cur.g + 1;
					next.h = heuristic(next, end);
				} else {
					if(cur.g + 1 < next.g || next.g < 0) {
						next.parent = cur;
						next.g = cur.g + 1;
						next.h = heuristic(next, end);
					}
				}
			}
		}

		return -1;
	}

	private static int heuristic(Node cur, Node end) {
		return Math.abs(end.x - cur.x) + Math.abs(end.y - cur.y);
	}

static class Node {
	int x;
	int y;
	int g;
	int h;
	boolean object;
	Node parent;

	public Node(int x, int y, int g, int h, boolean object) {
		this.x = x;
		this.y = y;
		this.g = g;
		this.h = h;
		this.object = object;
		this.parent = null;
	}

	public static Node[][] createGrid(int x, int y){
		Node[][] grid = new Node[x][y];
		for(int i = 0; i < x; i++) {
			for(int j = 0; j < y; j++) {
				grid[i][j] = new Node(i, j, -1, -1, false);
			}
		}
		return grid;
	}
}




}
