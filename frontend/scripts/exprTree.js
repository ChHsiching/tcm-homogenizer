/*
 * 符号表达式树 - 解析与规范化（步骤一）
 *
 * 本模块仅负责：
 *  - 将回归表达式字符串解析为 AST（仅 + - * / 与括号、数字、变量名）
 *  - AST 规范化：一元负号处理、同类运算扁平化、系数下沉（const * VAR → 变量叶子携带 coefficient）
 *  - AST → 表达式字符串（用于调试与后续联动公式刷新）
 *
 * 不依赖任何第三方库，可直接在浏览器/Electron 环境加载。
 */

(function initExprTreeModule() {
  const GLOBAL = (typeof window !== 'undefined') ? window : globalThis;

  // 公开 API 容器
  const ExprTree = {};

  // =============================
  // 基础工具
  // =============================
  let nodeIdSeq = 0;
  function nextNodeId(prefix = 'n') {
    nodeIdSeq += 1;
    return `${prefix}_${Date.now().toString(36)}_${nodeIdSeq}`;
  }

  function isDigit(ch) {
    const code = ch.charCodeAt(0);
    return code >= 48 && code <= 57; // 0-9
  }

  function isIdentStart(ch) {
    const code = ch.charCodeAt(0);
    return (code >= 65 && code <= 90) || // A-Z
           (code >= 97 && code <= 122) || // a-z
           ch === '_';
  }

  function isIdentPart(ch) {
    return isIdentStart(ch) || isDigit(ch);
  }

  function formatNumberSci(value, fractionDigits = 4) {
    if (typeof value !== 'number' || !isFinite(value)) return String(value);
    const abs = Math.abs(value);
    if (abs !== 0 && (abs < 1e-3 || abs >= 1e4)) {
      return value.toExponential(4).toUpperCase();
    }
    return Number(value.toFixed(fractionDigits)).toString();
  }

  // =============================
  // 词法分析（Tokenizer）
  // =============================
  /**
   * 将表达式字符串拆分为 token 序列。
   * 支持：数字（含小数）、变量名（字母/下划线开头）、括号、运算符 + - * /。
   * 一元负号在 toRpn 中处理（识别 "u-"）。
   */
  function tokenize(expression) {
    const tokens = [];
    const src = String(expression || '').trim();
    const length = src.length;
    let i = 0;

    function lastToken() { return tokens.length ? tokens[tokens.length - 1] : null; }

    while (i < length) {
      const ch = src[i];

      // 跳过空白
      if (ch === ' ' || ch === '\t' || ch === '\n' || ch === '\r') {
        i += 1;
        continue;
      }

      // 处理以负号开头的数字（将其作为一个负常数，不拆成一元负号）
      if (ch === '-' && i + 1 < length && (isDigit(src[i + 1]) || (src[i + 1] === '.' && i + 2 < length && isDigit(src[i + 2])))) {
        const prev = lastToken();
        const isUnaryContext = !prev || prev.type === 'op' || prev.type === 'lparen';
        if (isUnaryContext) {
          let j = i + 1;
          let hasDot = (src[j] === '.');
          j += 1;
          while (j < length) {
            const c = src[j];
            if (isDigit(c)) { j += 1; continue; }
            if (c === '.' && !hasDot) { hasDot = true; j += 1; continue; }
            break;
          }
          const numText = src.slice(i, j); // 包含负号
          tokens.push({ type: 'number', value: parseFloat(numText) });
          i = j;
          continue;
        }
      }

      // 数字（含小数）
      if (isDigit(ch) || (ch === '.' && i + 1 < length && isDigit(src[i + 1]))) {
        let j = i;
        let hasDot = (ch === '.');
        j += 1;
        while (j < length) {
          const c = src[j];
          if (isDigit(c)) {
            j += 1;
          } else if (c === '.' && !hasDot) {
            hasDot = true;
            j += 1;
          } else {
            break;
          }
        }
        const numText = src.slice(i, j);
        tokens.push({ type: 'number', value: parseFloat(numText) });
        i = j;
        continue;
      }

      // 标识符（变量）
      if (isIdentStart(ch)) {
        let j = i + 1;
        while (j < length && isIdentPart(src[j])) j += 1;
        const ident = src.slice(i, j);
        tokens.push({ type: 'ident', value: ident });
        i = j;
        continue;
      }

      // 括号
      if (ch === '(') { tokens.push({ type: 'lparen', value: '(' }); i += 1; continue; }
      if (ch === ')') { tokens.push({ type: 'rparen', value: ')' }); i += 1; continue; }

      // 运算符
      if (ch === '+' || ch === '-' || ch === '*' || ch === '/') {
        tokens.push({ type: 'op', value: ch });
        i += 1;
        continue;
      }

      // 其他字符：直接作为未知，防止死循环
      tokens.push({ type: 'unknown', value: ch });
      i += 1;
    }

    return tokens;
  }

  // =============================
  // Shunting-yard: 中缀 → 后缀（RPN）
  // =============================
  function toRpn(tokens) {
    // 处理一元负号：
    // prev 为 null、op、lparen 时遇到 '-'，且后续不是数字连写（如 5-3），当作一元。
    const processed = [];
    let prev = null;
    for (let idx = 0; idx < tokens.length; idx += 1) {
      const t = tokens[idx];
      if (t.type === 'op' && t.value === '-') {
        const isUnary = !prev || prev.type === 'op' || prev.type === 'lparen';
        if (isUnary) {
          processed.push({ type: 'op', value: 'u-' });
          prev = { type: 'op', value: 'u-' };
          continue;
        }
      }
      processed.push(t);
      prev = t;
    }

    const out = [];
    const stack = [];

    function prec(op) {
      if (op === 'u-') return 3; // 一元负号最高
      if (op === '*' || op === '/') return 2;
      if (op === '+' || op === '-') return 1;
      return 0;
    }

    function isLeftAssoc(op) {
      if (op === 'u-') return false; // 视为右结合
      return true; // 其余全为左结合
    }

    for (const t of processed) {
      if (t.type === 'number' || t.type === 'ident') {
        out.push(t);
        continue;
      }
      if (t.type === 'op') {
        const o1 = t.value;
        if (o1 === 'u-') {
          // 我们已经在tokenize阶段将以负号起始的数字识别为负常数，
          // 因此这里保留一元负号仅用于对变量/括号表达式取反。
        }
        while (stack.length) {
          const top = stack[stack.length - 1];
          if (top.type === 'op') {
            const o2 = top.value;
            if ((isLeftAssoc(o1) && prec(o1) <= prec(o2)) || (!isLeftAssoc(o1) && prec(o1) < prec(o2))) {
              out.push(stack.pop());
              continue;
            }
          }
          break;
        }
        stack.push(t);
        continue;
      }
      if (t.type === 'lparen') { stack.push(t); continue; }
      if (t.type === 'rparen') {
        let found = false;
        while (stack.length) {
          const sTop = stack.pop();
          if (sTop.type === 'lparen') { found = true; break; }
          out.push(sTop);
        }
        if (!found) {
          throw new Error('括号不匹配：缺少左括号');
        }
        continue;
      }
      if (t.type === 'unknown') {
        throw new Error(`无法识别的字符: ${t.value}`);
      }
    }

    while (stack.length) {
      const sTop = stack.pop();
      if (sTop.type === 'lparen' || sTop.type === 'rparen') {
        throw new Error('括号不匹配：缺少右括号');
      }
      out.push(sTop);
    }

    return out;
  }

  // =============================
  // RPN → AST
  // =============================
  function rpnToAst(rpnTokens) {
    const stack = [];

    function makeConstant(value) {
      return {
        id: nextNodeId('c'),
        kind: 'constant',
        value: Number(value),
        children: []
      };
    }

    function makeVariable(name) {
      return {
        id: nextNodeId('v'),
        kind: 'variable',
        value: String(name),
        coefficient: 1,
        children: []
      };
    }

    function makeOperator(op, left, right) {
      const map = { '+': 'add', '-': 'sub', '*': 'mul', '/': 'div' };
      const opKind = map[op];
      if (!opKind) throw new Error(`未知运算符: ${op}`);
      return {
        id: nextNodeId('o'),
        kind: 'operator',
        op: opKind,
        children: [left, right]
      };
    }

    for (const t of rpnTokens) {
      if (t.type === 'number') {
        stack.push(makeConstant(t.value));
        continue;
      }
      if (t.type === 'ident') {
        stack.push(makeVariable(t.value));
        continue;
      }
      if (t.type === 'op') {
        if (t.value === 'u-') {
          // 一元负号：等价于 (-1) * x
          const a = stack.pop();
          if (!a) throw new Error('表达式错误：一元负号缺少操作数');
          const minusOne = makeConstant(-1);
          const node = makeOperator('*', minusOne, a);
          stack.push(node);
          continue;
        }
        const b = stack.pop();
        const a = stack.pop();
        if (!a || !b) throw new Error('表达式错误：二元运算缺少操作数');
        stack.push(makeOperator(t.value, a, b));
        continue;
      }
    }

    if (stack.length !== 1) {
      throw new Error('表达式错误：无法归约为单一 AST');
    }
    return stack[0];
  }

  // =============================
  // 规范化（扁平化 + 系数下沉）
  // =============================
  function cloneNode(node) {
    return JSON.parse(JSON.stringify(node));
  }

  function flattenSameOperator(node) {
    if (!node || node.kind !== 'operator') return node;

    node.children = node.children.map(flattenSameOperator);

    // 扁平化：add(add(a,b), c) → add(a,b,c)
    if (node.op === 'add' || node.op === 'mul') {
      const flatChildren = [];
      for (const ch of node.children) {
        if (ch.kind === 'operator' && ch.op === node.op) {
          flatChildren.push(...ch.children);
        } else {
          flatChildren.push(ch);
        }
      }
      node.children = flatChildren;
    }
    return node;
  }

  function sinkCoefficient(node) {
    if (!node || node.kind !== 'operator') return node;
    node.children = node.children.map(sinkCoefficient);

    // 仅处理乘法二元情况：const * var → variable{coefficient *= const}
    if (node.op === 'mul' && node.children.length === 2) {
      const left = node.children[0];
      const right = node.children[1];

      const isConstVar = (a, b) => a && b && a.kind === 'constant' && b.kind === 'variable';

      if (isConstVar(left, right)) {
        const v = cloneNode(right);
        const c = Number(left.value);
        const coef = typeof v.coefficient === 'number' ? v.coefficient : 1;
        v.coefficient = coef * c;
        return v;
      }
      if (isConstVar(right, left)) {
        const v = cloneNode(left);
        const c = Number(right.value);
        const coef = typeof v.coefficient === 'number' ? v.coefficient : 1;
        v.coefficient = coef * c;
        return v;
      }
    }
    return node;
  }

  function normalizeAst(ast) {
    // 深拷贝，避免外部引用被修改
    let node = cloneNode(ast);
    // 保持原始的二叉树结构，不再扁平化加法/乘法，
    // 以与后端给出的参考结构保持一致，避免形状差异
    node = sinkCoefficient(node);
    return node;
  }

  // ===============
  // AST 操作工具
  // ===============
  function makeConst(value) {
    return { id: nextNodeId('c'), kind: 'constant', value: Number(value), children: [] };
  }
  function makeOp(op, left, right) {
    return { id: nextNodeId('o'), kind: 'operator', op, children: [left, right] };
  }
  function isConst(node, val = undefined) {
    if (!node || node.kind !== 'constant') return false;
    if (val === undefined) return true;
    return Math.abs(Number(node.value) - Number(val)) < 1e-12;
  }
  function isVar(node) { return node && node.kind === 'variable'; }

  function negateNode(n) {
    if (isConst(n)) return makeConst(-Number(n.value));
    return makeOp('mul', makeConst(-1), n);
  }

  function simplifyAst(node) {
    if (!node) return makeConst(0);
    if (node.kind !== 'operator') return node;
    const a = simplifyAst(cloneNode(node.children[0]));
    const b = simplifyAst(cloneNode(node.children[1]));
    const op = node.op;
    // 规则：
    if (op === 'add') {
      if (isConst(a, 0)) return b;
      if (isConst(b, 0)) return a;
      return { id: node.id, kind: 'operator', op, children: [a, b] };
    }
    if (op === 'sub') {
      if (isConst(b, 0)) return a;
      if (isConst(a, 0)) return negateNode(b);
      return { id: node.id, kind: 'operator', op, children: [a, b] };
    }
    if (op === 'mul') {
      if (isConst(a, 0) || isConst(b, 0)) return makeConst(0);
      if (isConst(a, 1)) return b;
      if (isConst(b, 1)) return a;
      // 系数下沉：const * var
      if (isConst(a) && isVar(b)) {
        const v = cloneNode(b); v.coefficient = (typeof v.coefficient === 'number' ? v.coefficient : 1) * Number(a.value); return v;
      }
      if (isConst(b) && isVar(a)) {
        const v = cloneNode(a); v.coefficient = (typeof v.coefficient === 'number' ? v.coefficient : 1) * Number(b.value); return v;
      }
      return { id: node.id, kind: 'operator', op, children: [a, b] };
    }
    if (op === 'div') {
      if (isConst(a, 0)) return makeConst(0);
      if (isConst(b, 1)) return a;
      return { id: node.id, kind: 'operator', op, children: [a, b] };
    }
    return { id: node.id, kind: 'operator', op, children: [a, b] };
  }

  function deleteNodeById(root, targetId) {
    function remove(node) {
      if (!node) return { node: null, changed: false };
      if (node.id === targetId) {
        // 在父层处理，根结点的删除上层会特别处理
        return { node, changed: false, selfHit: true };
      }
      if (node.kind !== 'operator') return { node, changed: false };
      let left = node.children[0];
      let right = node.children[1];
      if (left && left.id === targetId) {
        const res = afterChildRemoved(node.op, right, 'left');
        return { node: simplifyAst(res), changed: true };
      }
      if (right && right.id === targetId) {
        const res = afterChildRemoved(node.op, left, 'right');
        return { node: simplifyAst(res), changed: true };
      }
      const r1 = remove(left); if (r1.changed) left = r1.node;
      const r2 = remove(right); if (r2.changed) right = r2.node;
      const out = { id: node.id, kind: 'operator', op: node.op, children: [left, right] };
      return { node: simplifyAst(out), changed: r1.changed || r2.changed };
    }
    function afterChildRemoved(op, other, removedSide) {
      if (op === 'add' || op === 'mul') return other;
      if (op === 'sub') return (removedSide === 'left') ? negateNode(other) : other;
      if (op === 'div') return (removedSide === 'left') ? makeConst(0) : other; // 删除分母→1等价于去掉除法
      return other;
    }
    // 根节点特殊处理
    if (root && root.id === targetId) {
      return makeConst(0);
    }
    const result = remove(cloneNode(root));
    return result.changed ? result.node : root;
  }

  ExprTree.cloneAst = cloneNode;
  ExprTree.simplifyAst = simplifyAst;
  ExprTree.deleteNodeById = deleteNodeById;

  // =============================
  // AST → 表达式字符串（用于调试和右上公式刷新）
  // =============================
  function astToExpression(node) {
    if (!node) return '0';
    if (node.kind === 'constant') {
      return formatNumberSci(Number(node.value), 6);
    }
    if (node.kind === 'variable') {
      const coef = (typeof node.coefficient === 'number') ? node.coefficient : 1;
      if (coef === 1) return String(node.value);
      if (coef === -1) return `-1 * ${node.value}`;
      return `${formatNumberSci(coef, 6)} * ${node.value}`;
    }
    if (node.kind === 'operator') {
      const [a, b] = node.children || [];
      const exprA = astToExpression(a);
      const exprB = astToExpression(b);
      if (node.op === 'add') return `${exprA} + ${exprB}`;
      // 在减法中，如果右孩子本身带有负号（负常数或负系数变量，或-1乘子），
      // 为避免出现 "A - -B" 的双负号，悬浮窗等文本表达中将其转为 "A - B" 形式。
      if (node.op === 'sub') {
        const exprBAdjusted = expressionForSubRight(b);
        return `${exprA} - ${exprBAdjusted}`;
      }
      if (node.op === 'mul') return `${maybeParen(a, node.op)} * ${maybeParen(b, node.op)}`;
      if (node.op === 'div') return `${maybeParen(a, node.op)} / ${maybeParen(b, node.op)}`;
    }
    return '0';
  }

  // 在减法中用于格式化右侧被减数，移除其“自身携带的负号”，保留减法运算符的负号语义
  function expressionForSubRight(n) {
    if (!n) return '0';
    // 常数：输出绝对值
    if (n.kind === 'constant') {
      const v = Number(n.value);
      return formatNumberSci(Math.abs(v), 6);
    }
    // 变量：若系数为负，改为其绝对值；-1 则省略为变量本身
    if (n.kind === 'variable') {
      const coef = (typeof n.coefficient === 'number') ? n.coefficient : 1;
      if (coef < 0) {
        const absCoef = Math.abs(coef);
        if (absCoef === 1) return String(n.value);
        return `${formatNumberSci(absCoef, 6)} * ${n.value}`;
      }
      if (coef === 1) return String(n.value);
      if (coef === -1) return String(n.value);
      return `${formatNumberSci(coef, 6)} * ${n.value}`;
    }
    // 乘法：若含负常数因子，去除其负号
    if (n.kind === 'operator' && n.op === 'mul' && n.children && n.children.length === 2) {
      const a = n.children[0];
      const b = n.children[1];
      if (a && a.kind === 'constant' && Number(a.value) < 0) {
        const k = Math.abs(Number(a.value));
        const right = maybeParen(b, 'mul');
        if (k === 1) return right;
        return `${formatNumberSci(k, 6)} * ${right}`;
      }
      if (b && b.kind === 'constant' && Number(b.value) < 0) {
        const k = Math.abs(Number(b.value));
        const left = maybeParen(a, 'mul');
        if (k === 1) return left;
        return `${formatNumberSci(k, 6)} * ${left}`;
      }
    }
    // 其他情况：保持原有表达
    return astToExpression(n);
  }

  function maybeParen(node, parentOp) {
    if (!node || node.kind !== 'operator') return astToExpression(node);
    // 乘/除的孩子如果是加/减需要加括号
    if ((parentOp === 'mul' || parentOp === 'div') && (node.op === 'add' || node.op === 'sub')) {
      return `(${astToExpression(node)})`;
    }
    // 保持除法的分母整体为一棵子树，不做进一步括号去除
    return astToExpression(node);
  }

  // 生成 LaTeX（含 align* 与前缀变量）
  function astToLatex(ast, target = 'Y') {
    function core(n, parentOp) {
      if (!n) return '0';
      if (n.kind === 'constant') return String(n.value);
      if (n.kind === 'variable') {
        const coef = (typeof n.coefficient === 'number') ? n.coefficient : 1;
        if (coef === 1) return String(n.value);
        if (coef === -1) return `-1 \\cdot ${n.value}`;
        return `${formatNumberSci(coef, 6)} \\cdot ${n.value}`;
      }
      const a = core(n.children[0], n.op);
      const b = core(n.children[1], n.op);
      if (n.op === 'add') return `${a} + ${b}`;
      if (n.op === 'sub') return `${a} - ${b}`;
      if (n.op === 'mul') {
        const la = (n.children[0].kind === 'operator' && (n.children[0].op === 'add' || n.children[0].op === 'sub')) ? `\\left(${a}\\right)` : a;
        const rb = (n.children[1].kind === 'operator' && (n.children[1].op === 'add' || n.children[1].op === 'sub')) ? `\\left(${b}\\right)` : b;
        return `${la} \\cdot ${rb}`;
      }
      if (n.op === 'div') return `\\cfrac{${a}}{${b}}`;
      return `${a} ${n.op} ${b}`;
    }
    const body = core(ast, null);
    return `\\begin{align*} \\nonumber ${target} &= ${body} \\end{align*}`;
  }
  ExprTree.astToLatex = astToLatex;

  // =============================
  // 公开 API
  // =============================
  function parseExpressionToAst(expression) {
    const tokens = tokenize(expression);
    const rpn = toRpn(tokens);
    const ast = rpnToAst(rpn);
    return ast;
  }

  ExprTree.parseExpressionToAst = parseExpressionToAst;
  ExprTree.normalizeAst = normalizeAst;
  ExprTree.astToExpression = astToExpression;
  ExprTree.formatNumberSci = formatNumberSci;
  
  // =============================
  // 影响力计算与颜色映射（V1）
  // =============================
  function computeWeights(root, options = {}) {
    const nodeList = [];

    // 若提供了节点级影响力树（docs/tree.json 的结构），使用它来覆盖叶子节点的影响力
    const externalMap = buildLeafImpactMapFromTree(GLOBAL.currentNodeImpactsTree);

    function dfs(node) {
      if (!node) return 0;
      nodeList.push(node);

      if (node.kind === 'constant') {
        // 常数叶子优先使用外部映射（若存在精确匹配的格式化文本）
        const key = formatLeafKey(node);
        if (externalMap && externalMap.has(key)) {
          node.weight = externalMap.get(key);
        } else {
          node.weight = 0;
        }
        return node.weight;
      }

      if (node.kind === 'variable') {
        // 变量叶子优先使用外部映射；否则按系数估计
        const key = formatLeafKey(node);
        if (externalMap && externalMap.has(key)) {
          node.weight = externalMap.get(key);
        } else {
          const coef = (typeof node.coefficient === 'number') ? node.coefficient : 1;
          node.weight = coef;
        }
        return node.weight;
      }

      // operator
      const children = node.children || [];
      const childWeights = children.map(ch => dfs(ch));

      if (node.op === 'add') {
        node.weight = childWeights.reduce((a, b) => a + b, 0);
        return node.weight;
      }
      if (node.op === 'sub') {
        if (childWeights.length === 0) { node.weight = 0; return node.weight; }
        if (childWeights.length === 1) { node.weight = childWeights[0]; return node.weight; }
        node.weight = childWeights[0] - childWeights[1];
        return node.weight;
      }
      if (node.op === 'mul') {
        // const * expr → 放大/缩小影响力；多个非常量子树时，简化为常量积 * 非常量影响力和
        let constProduct = 1;
        let nonConstChildren = [];
        for (const ch of children) {
          if (ch.kind === 'constant') constProduct *= Number(ch.value);
          else nonConstChildren.push(ch);
        }
        if (nonConstChildren.length === 0) {
          node.weight = 0; // 只有常数相乘
          return node.weight;
        }
        if (nonConstChildren.length === 1) {
          node.weight = constProduct * (nonConstChildren[0].weight ?? 0);
          return node.weight;
        }
        // 多个非常量：常量积 * 非常量影响力之和（近似）
        const sumNonConst = nonConstChildren.reduce((s, ch) => s + (ch.weight ?? 0), 0);
        node.weight = constProduct * sumNonConst;
        return node.weight;
      }
      if (node.op === 'div') {
        const [numerator, denominator] = children;
        const denomIsConstOnly = denominator && isConstOnlySubtree(denominator);
        if (denomIsConstOnly) {
          const denomVal = evalConstSubtree(denominator);
          node.weight = (numerator ? (numerator.weight ?? 0) : 0) / (denomVal || 1);
          return node.weight;
        }
        // 简化近似：分子影响力 − 分母影响力（方向性）
        node.weight = (numerator ? (numerator.weight ?? 0) : 0) - (denominator ? (denominator.weight ?? 0) : 0);
        return node.weight;
      }

      node.weight = 0;
      return node.weight;
    }

    function isConstOnlySubtree(node) {
      if (!node) return true;
      if (node.kind === 'constant') return true;
      if (node.kind === 'variable') return false;
      return (node.children || []).every(isConstOnlySubtree);
    }

    function evalConstSubtree(node) {
      if (!node) return 1;
      if (node.kind === 'constant') return Number(node.value);
      if (node.kind === 'variable') return 1; // 不应走到这里
      const [a, b] = node.children || [];
      if (node.op === 'add') return evalConstSubtree(a) + evalConstSubtree(b);
      if (node.op === 'sub') return evalConstSubtree(a) - evalConstSubtree(b);
      if (node.op === 'mul') return evalConstSubtree(a) * evalConstSubtree(b);
      if (node.op === 'div') return evalConstSubtree(a) / evalConstSubtree(b);
      return 1;
    }

    dfs(root);

    // 颜色映射：以 P95 的绝对值为 scale
    const absWeights = nodeList.map(n => Math.abs(n.weight || 0));
    const scale = quantile(absWeights, 0.95) || Math.max(...absWeights, 1);
    for (const n of nodeList) {
      n.color = weightToColor(n.weight || 0, scale);
    }

    return { scale, nodes: nodeList };
  }

  // 将 docs/tree.json 的嵌套对象拍平成 叶子表达式文本 → 影响力 的 Map
  function buildLeafImpactMapFromTree(treeObj) {
    if (!treeObj || typeof treeObj !== 'object') return null;
    const map = new Map();
    (function walk(obj) {
      if (!obj || typeof obj !== 'object') return;
      for (const [k, v] of Object.entries(obj)) {
        if (v !== null && typeof v === 'object') walk(v);
        else map.set(String(k), Number(v) || 0);
      }
    })(treeObj);
    return map;
  }

  function quantile(arr, q) {
    if (!arr || arr.length === 0) return 0;
    const a = [...arr].sort((x, y) => x - y);
    const pos = (a.length - 1) * q;
    const base = Math.floor(pos);
    const rest = pos - base;
    if ((a[base + 1] !== undefined)) {
      return a[base] + rest * (a[base + 1] - a[base]);
    } else {
      return a[base];
    }
  }

  function clamp(x, lo, hi) { return Math.min(hi, Math.max(lo, x)); }

  function weightToColor(weight, scale) {
    const w = Number(weight) || 0;
    const s = Math.max(Number(scale) || 1, 1e-9);
    const t = clamp(Math.abs(w) / s, 0, 1);
    const lightness = 95 - 60 * t; // 95% → 35%
    if (w > 0) {
      return `hsl(145, 60%, ${lightness}%)`;
    }
    if (w < 0) {
      return `hsl(0, 65%, ${lightness}%)`;
    }
    return '#ffffff';
  }

  ExprTree.computeWeights = computeWeights;
  ExprTree.weightToColor = weightToColor;

  // 将整棵树聚合为“特征影响力”列表（V1：按变量系数的绝对值累加并做归一化）
  function computeFeatureImportance(root) {
    const totals = new Map();
    (function walk(n) {
      if (!n) return;
      if (n.kind === 'variable') {
        const coef = (typeof n.coefficient === 'number') ? n.coefficient : 1;
        const key = String(n.value);
        const prev = totals.get(key) || 0;
        totals.set(key, prev + Math.abs(Number(coef)));
      }
      (n.children || []).forEach(walk);
    })(root);
    const arr = Array.from(totals.entries()).map(([feature, s]) => ({ feature, importance: Number(s) }));
    const total = arr.reduce((acc, x) => acc + x.importance, 0);
    if (total > 0) {
      for (const item of arr) {
        item.importance = Number((item.importance / total).toFixed(6));
      }
    }
    arr.sort((a, b) => b.importance - a.importance);
    return arr;
  }
  ExprTree.computeFeatureImportance = computeFeatureImportance;
  // 生成叶子表达式的匹配键：与 docs/tree.json 的叶子键一致
  function formatLeafKey(n) {
    if (!n) return '';
    if (n.kind === 'constant') {
      // docs/tree.json 中常数多以固定小数位，例如 "-10.458" 或 "0.0054"
      return String(formatNumberSci(Number(n.value), 4));
    }
    if (n.kind === 'variable') {
      const coef = (typeof n.coefficient === 'number') ? n.coefficient : 1;
      if (coef === 1) return String(n.value);
      return `${formatNumberSci(coef, 4)} * ${n.value}`;
    }
    return '';
  }

  // 运算符显示标签（布局与渲染共享）
  function operatorLabel(op) {
    return op === 'add' ? 'Addition'
      : op === 'sub' ? 'Subtraction'
      : op === 'mul' ? 'Multiplication'
      : op === 'div' ? 'Division'
      : String(op || '?');
  }

  // =============================
  // 简化树布局（自顶向下）
  // =============================
  function layoutTree(root, viewportW = 900, metrics = {}) {
    // 使用基础尺寸进行布局计算（不随显示缩放变化）
    const cfg = Object.assign({
      nodeRadius: 40,
      leafW: 110,
      leafH: 56,
      siblingGap: 24,
      vGap: 0,
      drawScale: 1,
      textScale: 2
    }, metrics || {});
    // 让相邻两层至少隔一个节点高度
    const baseH = Math.max(cfg.nodeRadius * 2, cfg.leafH);
    cfg.vGap = Math.max(cfg.vGap, baseH * 2);

    // 预度量：记录自身节点宽度（不含子树），以及子树块宽度w（用于分配水平空间）。
    function measure(node) {
      if (!node) return 0;
      const selfW = (node.kind === 'operator') ? cfg.nodeRadius * 2 : cfg.leafW;
      if (!node.children || node.children.length === 0) {
        node.layout = Object.assign(node.layout || {}, { wSelf: selfW, w: selfW, h: cfg.leafH });
        return selfW;
      }
      // 子树宽度基于子树块宽之和，保证每棵子树在父层预留足够水平空间，避免跨层交叉
      node.children.forEach(measure);
      const childrenSumW = node.children.reduce((s, ch) => s + (ch.layout?.w || ch.layout?.wSelf || selfW), 0);
      const childrenBlock = childrenSumW + cfg.siblingGap * (node.children.length - 1);
      const subW = Math.max(selfW, childrenBlock);
      node.layout = Object.assign(node.layout || {}, { wSelf: selfW, w: subW, h: cfg.leafH });
      return subW;
    }

    function assign(node, left, depth) {
      if (!node) return left;
      const lw = node.layout?.w || 0;      // 当前子树块宽度
      const selfW = node.layout?.wSelf || lw; // 当前节点自身宽度
      const centerX = left + lw / 2;
      node.layout = Object.assign(node.layout || {}, {
        x: centerX,
        y: depth * cfg.vGap
      });
      if (!node.children || node.children.length === 0) return left + lw;

      // 将同级子树按“子树块宽 + siblingGap”对称排列，父节点位于子块中心，保证不交叉
      const childrenSumW = node.children.reduce((s, ch) => s + (ch.layout?.w || ch.layout?.wSelf || selfW), 0);
      const block = childrenSumW + cfg.siblingGap * (node.children.length - 1);
      let cursor = centerX - block / 2; // 子块的最左
      for (const ch of node.children) {
        const cw = ch.layout?.w || ch.layout?.wSelf || selfW;
        assign(ch, cursor, depth + 1); // 子树以其块宽从cursor开始布局
        cursor += cw + cfg.siblingGap;
      }
      return left + lw;
    }

    function collectLevels(node, levelMap, depth) {
      if (!node) return;
      if (!levelMap[depth]) levelMap[depth] = [];
      levelMap[depth].push(node);
      (node.children || []).forEach(ch => collectLevels(ch, levelMap, depth + 1));
    }

    function shiftSubtree(node, dx) {
      if (!node) return;
      node.layout.x = (node.layout.x || 0) + dx;
      (node.children || []).forEach(ch => shiftSubtree(ch, dx));
    }

    function nodeBoundsX(node) {
      const half = (node.kind === 'operator') ? cfg.nodeRadius : cfg.leafW / 2;
      return { left: (node.layout.x || 0) - half, right: (node.layout.x || 0) + half };
    }

    function operatorHalfWidthEstimate(op) {
      // 动态估计胶囊宽度的一半（考虑文本长度与放大倍率），单位：布局坐标
      const fontSize = 12 * (cfg.textScale || 1);
      const text = operatorLabel(op);
      const pad = 12 * (cfg.textScale || 1);
      const estWidth = text.length * fontSize * 0.6 + 2 * pad; // 经验系数 0.6
      const minWidth = cfg.nodeRadius * 2 * (cfg.drawScale || 1);
      return Math.max(minWidth / 2, estWidth / 2);
    }

    function resolveCollisions(root) {
      const levels = {};
      collectLevels(root, levels, 0);
      Object.keys(levels).forEach(key => {
        const nodes = levels[key].slice().sort((a, b) => (a.layout.x || 0) - (b.layout.x || 0));
        let prevRight = -Infinity;
        for (const n of nodes) {
          const half = (n.kind === 'operator')
            ? operatorHalfWidthEstimate(n.op)
            : (cfg.leafW / 2) * (cfg.drawScale || 1);
          const left = (n.layout.x || 0) - half;
          const right = (n.layout.x || 0) + half;
          if (left < prevRight + cfg.siblingGap) {
            const dx = (prevRight + cfg.siblingGap) - left;
            shiftSubtree(n, dx);
            prevRight = right + dx;
          } else {
            prevRight = right;
          }
        }
      });
    }

    // 仅在指定层解决节点之间的最小间距，但不移动其子树（保持子树位置不变）
    function resolveNodeOnlyCollisionsAtLevel(nodes) {
      const list = nodes.slice().sort((a, b) => (a.layout.x || 0) - (b.layout.x || 0));
      let prevRight = -Infinity;
      for (const n of list) {
        const half = (n.kind === 'operator')
          ? operatorHalfWidthEstimate(n.op)
          : (cfg.leafW / 2) * (cfg.drawScale || 1);
        const left = (n.layout.x || 0) - half;
        const right = (n.layout.x || 0) + half;
        if (left < prevRight + cfg.siblingGap) {
          const dx = (prevRight + cfg.siblingGap) - left;
          n.layout.x = (n.layout.x || 0) + dx; // 只移动本节点
          prevRight = right + dx;
        } else {
          prevRight = right;
        }
      }
    }

    // 自底向上将父节点重心对齐到其左右最外子节点的中心点，保证对称
    function recenterParents(root) {
      const levels = {};
      collectLevels(root, levels, 0);
      const levelKeys = Object.keys(levels).map(n => parseInt(n, 10)).sort((a, b) => b - a); // 自底向上
      for (const d of levelKeys) {
        const nodes = levels[d] || [];
        for (const n of nodes) {
          if (!n.children || n.children.length === 0) continue;
          const leftmost = n.children[0];
          const rightmost = n.children[n.children.length - 1];
          const target = ((leftmost.layout?.x || 0) + (rightmost.layout?.x || 0)) / 2;
          n.layout.x = target; // 将父节点置于孩子中点
        }
        // 该层父节点之间保持最小间距，但不影响其子树位置
        resolveNodeOnlyCollisionsAtLevel(nodes);
      }
    }

    function computeBounds(root) {
      let minX = Infinity, maxX = -Infinity, maxDepth = 0;
      const visit = (n, d) => {
        const b = nodeBoundsX(n);
        if (b.left < minX) minX = b.left;
        if (b.right > maxX) maxX = b.right;
        if (d > maxDepth) maxDepth = d;
        (n.children || []).forEach(ch => visit(ch, d + 1));
      };
      visit(root, 0);
      return { minX, maxX, depth: maxDepth };
    }

    // 1) 初步布局（对称排列同级，子树使用自身块宽）
    measure(root);
    assign(root, 0, 0);
    // 2) 每层逐一消除重叠，最小保留 siblingGap（理论上已避免交叉，此步骤作为保险）
    resolveCollisions(root);

    // 3) 重新居中父节点，确保子树对称
    recenterParents(root);
    // 4) 居中后再次按放大后的半径进行一次同层碰撞修正，彻底避免放大导致的轻微重叠
    resolveCollisions(root);
    const { minX, maxX } = computeBounds(root);
    const totalW = Math.max(maxX - minX, viewportW);
    return { width: totalW, config: cfg, bounds: { minX, maxX } };
  }

  ExprTree.layoutTree = layoutTree;

  // =============================
  // SVG 渲染（零依赖）
  // =============================
  function renderSvgTree(containerEl, root, options = {}) {
    if (!containerEl) return null;
    // 渲染仍以基础尺寸为布局坐标，但绘制时单独使用放大倍率
    const cfg = Object.assign({
      nodeRadius: 40,
      leafW: 110,
      leafH: 56,
      vGap: 0,
      margin: { top: 24, right: 24, bottom: 24, left: 24 }
    }, options.config || {});
    // 兜底：计算最小层间距
    const baseH2 = Math.max(cfg.nodeRadius * 2, cfg.leafH);
    if (!cfg.vGap || cfg.vGap < baseH2 * 2) cfg.vGap = baseH2 * 2;

    // 显示放大倍率：节点尺寸 1.5x，字体 2x
    const NODE_SCALE = 1.5;
    const TEXT_SCALE = 2.0;
    const rDraw = cfg.nodeRadius * NODE_SCALE;
    const leafWDraw = cfg.leafW * NODE_SCALE;
    const leafHDraw = cfg.leafH * NODE_SCALE;

    // 使用 layoutTree 返回的 bounds 进行左偏移归一化，确保从0开始渲染
    const bounds = options.bounds || { minX: 0, maxX: (root.layout?.w || 900) };
    const innerWidth = Math.max(options.width || (bounds.maxX - bounds.minX) || (root.layout?.w || 900), 300);
    const depth = getMaxDepth(root);
    const height = cfg.margin.top + cfg.margin.bottom + (depth + 1) * cfg.vGap + cfg.nodeRadius; // 顶部为圆半径留白
    const totalWidth = cfg.margin.left + innerWidth + cfg.margin.right;

    // 清空容器
    while (containerEl.firstChild) containerEl.removeChild(containerEl.firstChild);

    const svgNS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    svg.setAttribute('viewBox', `0 0 ${totalWidth} ${height}`);
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    svg.style.display = 'block';
    containerEl.appendChild(svg);

    // 自定义 Tooltip 容器（替代浏览器原生 <title> 气泡）
    const tooltipHost = containerEl.parentElement || containerEl; // #expression-tree-canvas 为相对定位
    let tooltipEl = tooltipHost.querySelector('.expr-tooltip');
    if (!tooltipEl) {
      tooltipEl = document.createElement('div');
      tooltipEl.className = 'expr-tooltip';
      tooltipEl.style.display = 'none';
      tooltipEl.style.position = 'absolute';
      tooltipEl.style.pointerEvents = 'none';
      tooltipHost.appendChild(tooltipEl);
    }

    // 右键菜单容器（统一复用）
    let ctxMenu = tooltipHost.querySelector('.expr-context-menu');
    if (!ctxMenu) {
      ctxMenu = document.createElement('div');
      ctxMenu.className = 'expr-context-menu';
      ctxMenu.style.display = 'none';
      ctxMenu.style.position = 'absolute';
      tooltipHost.appendChild(ctxMenu);
    }

    // 连线层
    const linksLayer = document.createElementNS(svgNS, 'g');
    linksLayer.setAttribute('fill', 'none');
    linksLayer.setAttribute('stroke', '#6b7280');
    linksLayer.setAttribute('stroke-width', '1.5');
    svg.appendChild(linksLayer);

    // 节点层
    const nodesLayer = document.createElementNS(svgNS, 'g');
    svg.appendChild(nodesLayer);
    let selectedNodeId = null;

    // 绘制连线
    const xOffset = cfg.margin.left - (bounds.minX || 0);
    const yOffset = cfg.margin.top + cfg.nodeRadius; // 使根节点完全显示

    traverse(root, (node) => {
      if (!node || !node.children) return;
      const x1 = (node.layout?.x || 0) + xOffset;
      const y1 = (node.layout?.y || 0) + yOffset + (node.kind === 'operator' ? rDraw : leafHDraw / 2);
      for (const ch of node.children) {
        const x2 = (ch.layout?.x || 0) + xOffset;
        const y2 = (ch.layout?.y || 0) + yOffset - (ch.kind === 'operator' ? rDraw : leafHDraw / 2);
        const line = document.createElementNS(svgNS, 'line');
        line.setAttribute('x1', String(x1));
        line.setAttribute('y1', String(y1));
        line.setAttribute('x2', String(x2));
        line.setAttribute('y2', String(y2));
        line.setAttribute('stroke-linecap', 'round');
        linksLayer.appendChild(line);
      }
    });

    // 绘制节点
    traverse(root, (node) => {
      const g = document.createElementNS(svgNS, 'g');
      g.setAttribute('data-id', node.id);
      g.style.cursor = 'pointer';
      nodesLayer.appendChild(g);

      const x = (node.layout?.x || 0) + xOffset;
      const y = (node.layout?.y || 0) + yOffset;
      const color = node.color || '#ffffff';
      const stroke = '#1f2937';

      if (node.kind === 'operator') {
        const fontSize = 12 * TEXT_SCALE;
        const text = operatorLabel(node.op);
        const pad = 12 * TEXT_SCALE;
        const estWidth = text.length * fontSize * 0.6 + 2 * pad;
        const pillW = Math.max(2 * rDraw, estWidth);
        const pillH = 2 * rDraw;

        const rect = document.createElementNS(svgNS, 'rect');
        rect.setAttribute('x', String(x - pillW / 2));
        rect.setAttribute('y', String(y - pillH / 2));
        rect.setAttribute('width', String(pillW));
        rect.setAttribute('height', String(pillH));
        rect.setAttribute('rx', String(pillH / 2));
        rect.setAttribute('fill', color);
        rect.setAttribute('stroke', stroke);
        rect.setAttribute('stroke-width', '2');
        rect.setAttribute('data-node-id', node.id);
        g.appendChild(rect);

        const label = document.createElementNS(svgNS, 'text');
        label.setAttribute('x', String(x));
        label.setAttribute('y', String(y + fontSize * 0.33));
        label.setAttribute('text-anchor', 'middle');
        label.setAttribute('font-size', String(fontSize));
        label.setAttribute('fill', '#111827');
        label.textContent = text;
        g.appendChild(label);
      } else {
        const rect = document.createElementNS(svgNS, 'rect');
        rect.setAttribute('x', String(x - leafWDraw / 2));
        rect.setAttribute('y', String(y - leafHDraw / 2));
        rect.setAttribute('width', String(leafWDraw));
        rect.setAttribute('height', String(leafHDraw));
        rect.setAttribute('rx', '10');
        rect.setAttribute('fill', color);
        rect.setAttribute('stroke', stroke);
        rect.setAttribute('stroke-width', '2');
        rect.setAttribute('data-node-id', node.id);
        g.appendChild(rect);

        const t1 = document.createElementNS(svgNS, 'text');
        t1.setAttribute('x', String(x));
        t1.setAttribute('y', String(y - 4 * NODE_SCALE));
        t1.setAttribute('text-anchor', 'middle');
        t1.setAttribute('font-size', String(12 * TEXT_SCALE));
        t1.setAttribute('fill', '#111827');

        const t2 = document.createElementNS(svgNS, 'text');
        t2.setAttribute('x', String(x));
        t2.setAttribute('y', String(y + 24 * NODE_SCALE / 1.5));
        t2.setAttribute('text-anchor', 'middle');
        t2.setAttribute('font-size', String(12 * TEXT_SCALE));
        t2.setAttribute('fill', '#111827');

        if (node.kind === 'variable') {
          const coef = (typeof node.coefficient === 'number') ? node.coefficient : 1;
          const coefText = (coef === 1) ? '' : formatNumberSci(coef, 4);
          if (coefText) {
            t1.textContent = coefText;
            t2.textContent = String(node.value);
            g.appendChild(t1);
            g.appendChild(t2);
          } else {
            t1.setAttribute('y', String(y + 10 * NODE_SCALE / 1.5));
            t1.textContent = String(node.value);
            g.appendChild(t1);
          }
        } else if (node.kind === 'constant') {
          t1.setAttribute('y', String(y + 10 * NODE_SCALE / 1.5));
          t1.textContent = formatNumberSci(Number(node.value), 4);
          g.appendChild(t1);
        }
      }

      // 自定义 Tooltip 交互
      const subExpr = safeSubExpr(node);
      const weightStr = Number(node.weight || 0).toFixed(6);
      const cn = (typeof window !== 'undefined' && window.COMPONENT_NAMES && node.kind === 'variable') ? (window.COMPONENT_NAMES[String(node.value)] || '') : '';
      const dotColor = node.color || '#ffffff';

      const showTooltip = (ev) => {
        try {
          const exprHtml = escapeHtml(subExpr || '');
          const cnHtml = cn ? `<span class="expr-tooltip-name">${escapeHtml(cn)}</span>` : '';
          tooltipEl.innerHTML = `
            <div class="expr-tooltip-expr">${exprHtml}</div>
            <div class="expr-tooltip-meta">
              <span class="expr-tooltip-dot" style="background:${dotColor}"></span>
              <span>影响力: ${weightStr}</span>
              ${cnHtml}
            </div>
          `;
          tooltipEl.style.display = 'block';
          tooltipEl.style.borderLeft = `4px solid ${dotColor}`;
          positionTooltip(ev);
        } catch (_) {}
      };

      const positionTooltip = (ev) => {
        try {
          const hostRect = tooltipHost.getBoundingClientRect();
          const offset = 12;
          const desiredLeft = ev.clientX - hostRect.left + offset;
          const desiredTop = ev.clientY - hostRect.top + offset;
          // 放置后再进行边界修正
          tooltipEl.style.left = `${desiredLeft}px`;
          tooltipEl.style.top = `${desiredTop}px`;
          const tipRect = tooltipEl.getBoundingClientRect();
          let left = desiredLeft;
          let top = desiredTop;
          const maxLeft = hostRect.width - tipRect.width - 8;
          const maxTop = hostRect.height - tipRect.height - 8;
          if (left > maxLeft) left = Math.max(8, maxLeft);
          if (top > maxTop) top = Math.max(8, maxTop);
          if (left < 8) left = 8;
          if (top < 8) top = 8;
          tooltipEl.style.left = `${left}px`;
          tooltipEl.style.top = `${top}px`;
        } catch (_) {}
      };

      const hideTooltip = () => {
        tooltipEl.style.display = 'none';
      };

      g.addEventListener('mouseenter', showTooltip);
      g.addEventListener('mousemove', positionTooltip);
      g.addEventListener('mouseleave', hideTooltip);

      // 交互回调
      g.addEventListener('contextmenu', (ev) => {
        ev.preventDefault();
        // 隐藏悬浮窗
        hideTooltip();
        // 选中该节点
        try {
          const old = nodesLayer.querySelector('[data-selected="true"]');
          if (old) {
            old.removeAttribute('data-selected');
            old.setAttribute('stroke', '#1f2937');
            old.setAttribute('stroke-width', '2');
            old.setAttribute('filter', '');
          }
          const shape = g.querySelector('rect');
          if (shape) {
            shape.setAttribute('data-selected', 'true');
            shape.setAttribute('stroke', '#60a5fa');
            shape.setAttribute('stroke-width', '3');
            shape.setAttribute('filter', 'drop-shadow(0 0 6px rgba(96,165,250,0.65)) drop-shadow(0 0 14px rgba(96,165,250,0.35))');
            selectedNodeId = node.id;
          }
        } catch (_) {}

        // 渲染并显示右键菜单
        try {
          ctxMenu.innerHTML = '';
          const item = document.createElement('button');
          item.type = 'button';
          item.className = 'context-item danger';
          item.textContent = '删除节点/子树';
          item.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            ctxMenu.style.display = 'none';
            // 触发底部红色“删除节点/子树”按钮（已由外层绑定真实逻辑）
            const btn = tooltipHost.querySelector('#btn-delete');
            if (btn && typeof btn.click === 'function') btn.click();
          };
          ctxMenu.appendChild(item);

          const hostRect = tooltipHost.getBoundingClientRect();
          const offset = 2;
          let left = ev.clientX - hostRect.left + offset;
          let top = ev.clientY - hostRect.top + offset;
          ctxMenu.style.display = 'block';
          // 边界纠正
          const menuRect = ctxMenu.getBoundingClientRect();
          const maxLeft = hostRect.width - menuRect.width - 8;
          const maxTop = hostRect.height - menuRect.height - 8;
          if (left > maxLeft) left = Math.max(8, maxLeft);
          if (top > maxTop) top = Math.max(8, maxTop);
          if (left < 8) left = 8;
          if (top < 8) top = 8;
          ctxMenu.style.left = `${left}px`;
          ctxMenu.style.top = `${top}px`;

          const dismiss = (e2) => {
            // 点击在菜单外部则关闭
            try {
              if (!ctxMenu.contains(e2.target)) {
                ctxMenu.style.display = 'none';
                window.removeEventListener('click', dismiss, true);
                window.removeEventListener('scroll', dismiss, true);
                window.removeEventListener('resize', dismiss, true);
              }
            } catch (_) {}
          };
          window.addEventListener('click', dismiss, true);
          window.addEventListener('scroll', dismiss, true);
          window.addEventListener('resize', dismiss, true);
        } catch (_) {}
      });
      g.addEventListener('click', (ev) => {
        // 选中高亮：先清除旧选中
        const old = nodesLayer.querySelector('[data-selected="true"]');
        if (old) {
          old.removeAttribute('data-selected');
          old.setAttribute('stroke', '#1f2937');
          old.setAttribute('stroke-width', '2');
          old.setAttribute('filter', '');
        }
        const shape = g.querySelector('rect');
        if (shape) {
          shape.setAttribute('data-selected', 'true');
          shape.setAttribute('stroke', '#60a5fa'); // Tailwind蓝-400近似
          shape.setAttribute('stroke-width', '3');
          // 蓝色柔和外发光：两层淡蓝色阴影
          shape.setAttribute('filter', 'drop-shadow(0 0 6px rgba(96,165,250,0.65)) drop-shadow(0 0 14px rgba(96,165,250,0.35))');
          selectedNodeId = node.id;
        }
        try { options.onClick && options.onClick(node, ev); } catch (_) {}
      });
    });

    // 在SVG下方渲染操作按钮条
    try {
      const toolbar = document.createElement('div');
      toolbar.style.display = 'flex';
      toolbar.style.gap = '10px';
      toolbar.style.marginTop = '10px';

      const btns = [
        { text: '删除节点/子树', color: '#ef4444', id: 'btn-delete' },
        { text: '简化', color: '#10b981', id: 'btn-simplify' },
        { text: '优化', color: '#3b82f6', id: 'btn-optimize' },
        { text: '撤销', color: '#f59e0b', id: 'btn-undo' },
      ];
      btns.forEach(b => {
        const el = document.createElement('button');
        el.textContent = b.text;
        el.style.background = b.color;
        el.style.border = 'none';
        el.style.color = '#fff';
        el.style.padding = '8px 14px';
        el.style.borderRadius = '6px';
        el.style.cursor = 'pointer';
        el.style.fontWeight = '600';
        el.id = b.id;
        // 仅挂空实现，后续填充逻辑
        el.addEventListener('click', () => {
          console.log(`[ExprTree] 点击: ${b.text}, 当前选中:`, selectedNodeId);
        });
        toolbar.appendChild(el);
      });
      // 将按钮条插入到容器(非SVG)下方
      if (containerEl && containerEl.parentElement) {
        // 移除旧工具条避免重复
        const prev = containerEl.parentElement.querySelector('.expr-tree-toolbar');
        if (prev) prev.remove();
        toolbar.className = 'expr-tree-toolbar';
        containerEl.parentElement.appendChild(toolbar);
      }
    } catch (_) {}

    return svg;

    function traverse(n, visit) { if (!n) return; visit(n); (n.children || []).forEach(c => traverse(c, visit)); }
    function getMaxDepth(n) { if (!n) return 0; if (!n.children || n.children.length === 0) return 0; return 1 + Math.max(...n.children.map(getMaxDepth)); }
    function opToText(op) { return op === 'add' ? 'Addition' : op === 'sub' ? 'Subtraction' : op === 'mul' ? 'Multiplication' : op === 'div' ? 'Division' : String(op || '?'); }
    function safeSubExpr(n) { try { return astToExpression(n); } catch (_) { return ''; } }
    function escapeHtml(str) {
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }
  }

  ExprTree.renderSvgTree = renderSvgTree;

  GLOBAL.ExprTree = ExprTree;
})();

