import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';

console.log('🚀 Testing Tattletale build...\n');

// Check if all required files exist
const requiredFiles = [
  'package.json',
  'tsconfig.json',
  'webpack.main.config.js',
  'webpack.renderer.config.js',
  'src/main.ts',
  'src/preload.ts',
  'src/renderer/renderer.tsx',
  'src/renderer/App.tsx',
  'assets/logo.png',
  'assets/icon.png'
];

console.log('📁 Checking required files...');
let allFilesExist = true;

for (const file of requiredFiles) {
  const exists = fs.existsSync(path.join(process.cwd(), file));
  console.log(`${exists ? '✅' : '❌'} ${file}`);
  if (!exists) allFilesExist = false;
}

if (!allFilesExist) {
  console.error('\n❌ Some required files are missing!');
  process.exit(1);
}

console.log('\n📦 Checking package.json structure...');
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));

const requiredScripts = ['start', 'build', 'make'];
const missingScripts = requiredScripts.filter(script => !packageJson.scripts[script]);

if (missingScripts.length > 0) {
  console.error(`\n❌ Missing scripts in package.json: ${missingScripts.join(', ')}`);
  process.exit(1);
} else {
  console.log('✅ All required scripts present');
}

const requiredDeps = ['@xenova/transformers', 'react', 'react-dom'];
const requiredDevDeps = ['electron'];

const missingDeps = requiredDeps.filter(dep => !packageJson.dependencies[dep]);
const missingDevDeps = requiredDevDeps.filter(dep => !packageJson.devDependencies[dep]);

if (missingDeps.length > 0) {
  console.error(`\n❌ Missing dependencies: ${missingDeps.join(', ')}`);
  process.exit(1);
} else {
  console.log('✅ All required dependencies present');
}

if (missingDevDeps.length > 0) {
  console.error(`\n❌ Missing devDependencies: ${missingDevDeps.join(', ')}`);
  process.exit(1);
} else {
  console.log('✅ All required devDependencies present');
}

console.log('\n🔧 Checking TypeScript configuration...');
const tsConfig = JSON.parse(fs.readFileSync('tsconfig.json', 'utf8'));

if (tsConfig.compilerOptions.target !== 'ES2020') {
  console.warn('⚠️  TypeScript target is not ES2020');
}

console.log('\n🎨 Checking assets...');
const assetsDir = path.join(process.cwd(), 'assets');
if (fs.existsSync(assetsDir)) {
  const files = fs.readdirSync(assetsDir);
  console.log(`✅ Assets directory contains ${files.length} files`);
} else {
  console.error('❌ Assets directory not found');
}

console.log('\n✅ Build test completed successfully!');
console.log('\nNext steps:');
console.log('1. Run: npm install');
console.log('2. Run: npm run build');
console.log('3. Run: npm start (for development)');
console.log('4. Run: npm run make (to create installers)');