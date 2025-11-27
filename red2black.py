# Simple Red-AVL hybrid node + tree (educational)
# RED, BLACK = True, False

class Node:
    def __init__(self, key, val=None, confidence=1.0):
        self.key = key
        self.val = val
        self.left = None
        self.right = None
        self.parent = None
        self.color = RED
        self.height = 1
        self.confidence = confidence
        self.usage = 0
        self.tombstone = False
        self.streak_low = 0

    def update_height(self):
        lh = self.left.height if self.left else 0
        rh = self.right.height if self.right else 0
        self.height = 1 + max(lh, rh)
        return self.height

    def balance_factor(self):
        lh = self.left.height if self.left else 0
        rh = self.right.height if self.right else 0
        return (lh - rh)

class RedAVL:
    def __init__(self, prune_threshold=0.2, prune_streak=2):
        self.root = None
        self.prune_threshold = prune_threshold
        self.prune_streak = prune_streak

    # BST insert (simple)
    def _bst_insert(self, root, node):
        if root is None: return node
        if node.key < root.key:
            root.left = self._bst_insert(root.left, node)
            root.left.parent = root
        elif node.key > root.key:
            root.right = self._bst_insert(root.right, node)
            root.right.parent = root
        else:
            # replace value & update confidence
            root.val = node.val
            root.confidence = node.confidence
            return root
        root.update_height()
        return root

    def insert(self, key, val=None, confidence=1.0):
        node = Node(key, val, confidence)
        if self.root is None:
            node.color = BLACK
            self.root = node
            return
        self.root = self._bst_insert(self.root, node)
        # quick simplistic rebalance: do AVL rotations if needed
        self._rebalance_up(node.parent or node)

    def _rotate_left(self, x):
        y = x.right
        if not y: return
        x.right = y.left
        if y.left: y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        x.update_height(); y.update_height()

    def _rotate_right(self, x):
        y = x.left
        if not y: return
        x.left = y.right
        if y.right: y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
        x.update_height(); y.update_height()

    def _rebalance_up(self, node):
        cur = node
        while cur:
            cur.update_height()
            bf = cur.balance_factor()
            if bf > 1:
                if cur.left and cur.left.balance_factor() < 0:
                    self._rotate_left(cur.left)
                self._rotate_right(cur)
            elif bf < -1:
                if cur.right and cur.right.balance_factor() > 0:
                    self._rotate_right(cur.right)
                self._rotate_left(cur)
            cur = cur.parent

    def find(self, key):
        cur = self.root
        while cur:
            if key == cur.key:
                return cur
            cur = cur.left if key < cur.key else cur.right
        return None

    def mark_measurement(self, key, measured_conf):
        n = self.find(key)
        if not n: return
        n.confidence = measured_conf
        if measured_conf < self.prune_threshold:
            n.streak_low += 1
            if n.streak_low >= self.prune_streak:
                self.delete(key)
        else:
            n.streak_low = 0

    def _transplant(self, u, v):
        if u.parent is None:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        if v: v.parent = u.parent

    def _min_node(self, x):
        while x.left: x = x.left
        return x

    def delete(self, key):
        z = self.find(key)
        if z is None: return
        if z.left is None:
            self._transplant(z, z.right)
        elif z.right is None:
            self._transplant(z, z.left)
        else:
            y = self._min_node(z.right)
            if y.parent is not z:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.update_height()
        # best-effort rebalance from parent
        p = (z.parent or self.root)
        if p: self._rebalance_up(p)
