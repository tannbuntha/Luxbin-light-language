/**
 * LUXBIN JavaScript AST Parser
 * Developed by Nicheai - JavaScript AST Parsing for Code Translation
 *
 * Uses esprima to parse JavaScript code into AST format
 * for cross-language translation.
 *
 * Company: Nicheai (https://nicheai.com)
 * Author: Nichole Christie
 * License: MIT
 */

const esprima = require('esprima');

/**
 * JavaScript AST Parser class
 */
class JsAstParser {
    constructor() {
        this.esprima = esprima;
    }

    /**
     * Parse JavaScript code into AST
     * @param {string} code - JavaScript source code
     * @returns {Object} AST object
     */
    parseCode(code) {
        try {
            return esprima.parseScript(code, {
                loc: true,
                range: true,
                tokens: true,
                comment: true
            });
        } catch (error) {
            throw new Error(`JavaScript parsing error: ${error.message}`);
        }
    }

    /**
     * Extract function declarations from AST
     * @param {Object} ast - Abstract Syntax Tree
     * @returns {Array} Array of function declarations
     */
    extractFunctions(ast) {
        const functions = [];

        function traverse(node, parent) {
            if (!node || typeof node !== 'object') return;

            if (node.type === 'FunctionDeclaration') {
                functions.push({
                    name: node.id ? node.id.name : 'anonymous',
                    params: node.params.map(param => param.name || 'param'),
                    body: node.body,
                    loc: node.loc
                });
            }

            // Traverse child nodes
            for (const key in node) {
                if (node.hasOwnProperty(key) && key !== 'parent') {
                    const child = node[key];
                    if (Array.isArray(child)) {
                        child.forEach(item => {
                            if (typeof item === 'object' && item !== null) {
                                item.parent = node;
                            }
                            traverse(item, node);
                        });
                    } else if (typeof child === 'object' && child !== null) {
                        child.parent = node;
                        traverse(child, node);
                    }
                }
            }
        }

        traverse(ast);
        return functions;
    }

    /**
     * Extract variable declarations from AST
     * @param {Object} ast - Abstract Syntax Tree
     * @returns {Array} Array of variable declarations
     */
    extractVariables(ast) {
        const variables = [];

        function traverse(node) {
            if (!node || typeof node !== 'object') return;

            if (node.type === 'VariableDeclaration') {
                node.declarations.forEach(decl => {
                    if (decl.id && decl.id.name) {
                        variables.push({
                            name: decl.id.name,
                            kind: node.kind, // var, let, const
                            init: decl.init,
                            loc: decl.loc
                        });
                    }
                });
            }

            // Traverse child nodes
            for (const key in node) {
                if (node.hasOwnProperty(key)) {
                    const child = node[key];
                    if (Array.isArray(child)) {
                        child.forEach(traverse);
                    } else if (typeof child === 'object' && child !== null) {
                        traverse(child);
                    }
                }
            }
        }

        traverse(ast);
        return variables;
    }

    /**
     * Analyze types in JavaScript code
     * @param {string} code - JavaScript source code
     * @returns {Object} Type analysis results
     */
    analyzeTypes(code) {
        const ast = this.parseCode(code);
        const types = {};

        function inferType(node) {
            if (!node) return 'unknown';

            switch (node.type) {
                case 'Literal':
                    if (typeof node.value === 'string') return 'string';
                    if (typeof node.value === 'number') return 'number';
                    if (typeof node.value === 'boolean') return 'boolean';
                    if (node.value === null) return 'null';
                    return 'unknown';

                case 'ArrayExpression':
                    return 'Array';

                case 'ObjectExpression':
                    return 'Object';

                case 'FunctionExpression':
                case 'ArrowFunctionExpression':
                    return 'Function';

                case 'NewExpression':
                    return node.callee.name || 'Object';

                default:
                    return 'unknown';
            }
        }

        // Extract variable types
        const variables = this.extractVariables(ast);
        variables.forEach(variable => {
            if (variable.init) {
                types[variable.name] = {
                    kind: variable.kind,
                    type: inferType(variable.init),
                    inferred: true
                };
            }
        });

        return types;
    }

    /**
     * Convert JavaScript AST to a simplified format for Python processing
     * @param {Object} ast - JavaScript AST
     * @returns {Object} Simplified AST structure
     */
    simplifyAst(ast) {
        return {
            type: ast.type,
            body: ast.body ? ast.body.map(node => this._simplifyNode(node)) : [],
            sourceType: ast.sourceType,
            tokens: ast.tokens,
            comments: ast.comments
        };
    }

    _simplifyNode(node) {
        if (!node) return null;

        const simplified = {
            type: node.type,
            loc: node.loc
        };

        // Copy relevant properties based on node type
        switch (node.type) {
            case 'FunctionDeclaration':
                simplified.id = node.id ? { name: node.id.name } : null;
                simplified.params = node.params ? node.params.map(p => ({ name: p.name })) : [];
                simplified.body = node.body ? this._simplifyNode(node.body) : null;
                break;

            case 'VariableDeclaration':
                simplified.kind = node.kind;
                simplified.declarations = node.declarations ? node.declarations.map(this._simplifyNode.bind(this)) : [];
                break;

            case 'VariableDeclarator':
                simplified.id = node.id ? this._simplifyNode(node.id) : null;
                simplified.init = node.init ? this._simplifyNode(node.init) : null;
                break;

            case 'Identifier':
                simplified.name = node.name;
                break;

            case 'Literal':
                simplified.value = node.value;
                simplified.raw = node.raw;
                break;

            case 'BlockStatement':
                simplified.body = node.body ? node.body.map(this._simplifyNode.bind(this)) : [];
                break;

            default:
                // For other node types, copy all properties that are not objects
                for (const key in node) {
                    if (node.hasOwnProperty(key) && typeof node[key] !== 'object') {
                        simplified[key] = node[key];
                    }
                }
                break;
        }

        return simplified;
    }
}

module.exports = JsAstParser;