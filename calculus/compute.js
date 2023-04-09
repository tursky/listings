// JS calculus
'use strict';

console.info(`
/** 
 * Trigonometric computations */
`);

// Dataset
const degrees = [0, 15, 30, 60, 75, 90, 105, 120, 135, 150, 165, 180];

// Degrees to radians
const rad = (deg) => deg * Math.PI / 180;

// Trigonometric math fns
const cos = (x) => Math.cos(rad(x));
const sin = (x) => Math.sin(rad(x));
const exp = (x) => Math.sqrt(sin(x) + 1/2);

// Output
const style = {
  rad: '\x1b[37m',  // white
  sin: '\x1b[31m',  // red
  cos: '\x1b[34m',  // blue
  exp: '\x1b[32m',  // green
};

// Lib
const curry = (fn) => (...args) => {
  if (fn.length > args.length) {
    const λ = fn.bind(null, ...args);
    return curry(λ);
  } else {
    return fn(...args);
  }
};

const cout = (χ) => console.log(χ);

let Σ = String;

// Computing
const compute = (fns) => {
  const formuala = (coefficient, operator, value, result) =>
    Σ(coefficient + operator + '(' + value + ')' + ' = ' + result);
  const φ = curry(formuala);

  const report = ({ Ορ, Vα, Rϵ }, Δ = 0.1, ω = ' ~ ') => {
    if (Δ) ω = style[Ορ];
    const τ = φ(ω)(Ορ, Vα, Rϵ);
    cout(τ);
  };

  for (const fn of fns) {
    cout(
      '',
      degrees.forEach((value) => 
        report({ Ορ: fn.name, Vα: value, Rϵ: fn(value) }))
    );
  };
};

const scenario = [rad, sin, cos, exp];

// Run
compute(scenario);