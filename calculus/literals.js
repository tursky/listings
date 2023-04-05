// Literals without $ using py-notation

const XXI = 'XXI';

const Σ = (array) => array.join('');
const f = (...n) => Σ(n);

const greeting = f('Welcome to the ', XXI, ' century!');   // `Welcome to the ${XXI} century!`

console.log(greeting);