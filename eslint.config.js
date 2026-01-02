import base from './ai_slop_gate/rulesets/eslint/base.mjs';
import secrets from './ai_slop_gate/rulesets/eslint/secrets.mjs';
import prodSafety from './ai_slop_gate/rulesets/eslint/prod_safety.mjs';

export default [
    {
        ignores: ["node_modules/", "venv/"]
    },
    ...base,
    ...secrets,
    ...prodSafety
];
