/**
 * Cute Cat Avatar Generator
 * Generates rich, adorable SVG cat faces with customizable breeds & expressions
 */
const CuteCats = {
  breeds: [
    { name: 'Calico', fur: '#FFEAA7', patch: '#E17055', darkPatch: '#2D3436', innerEar: '#FF7675', eyeColor: '#2D3436' },
    { name: 'Orange Tabby', fur: '#FAB1A0', patch: '#E17055', darkPatch: '#D63031', innerEar: '#FF7675', eyeColor: '#2D3436' },
    { name: 'Siamese', fur: '#F5E6CC', patch: '#634735', darkPatch: '#443024', innerEar: '#E8A87C', eyeColor: '#0984E3' },
    { name: 'Tuxedo', fur: '#2D3436', patch: '#FFFFFF', darkPatch: '#1E272E', innerEar: '#FF7675', eyeColor: '#2ED573' },
    { name: 'Pastel Pink', fur: '#FFD2DC', patch: '#FF88A5', darkPatch: '#FF5E7E', innerEar: '#FFAAB9', eyeColor: '#6C5CE7' },
    { name: 'Matcha Cream', fur: '#E2F0D9', patch: '#A8DADC', darkPatch: '#457B9D', innerEar: '#FFB7B2', eyeColor: '#2D3436' }
  ],

  getCatSvg(row, col, state = 'happy', size = 64) {
    // Pick deterministic breed based on row+col for visual variety
    const breedIdx = (row * 3 + col) % CuteCats.breeds.length;
    const b = CuteCats.breeds[breedIdx];

    // State can be: 'happy', 'conflict', 'testing', 'safe', 'crowned'
    let eyesSvg = '';
    let mouthSvg = '';
    let extraAccents = '';
    let bodyFilter = '';

    if (state === 'conflict') {
      // Angry/Shocked expression: > < eyes or wide alarmed pupils, squiggly mouth
      eyesSvg = `
        <!-- Left eye alarmed >_< -->
        <path d="M 28 42 L 36 47 L 28 52" fill="none" stroke="#D63031" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
        <!-- Right eye alarmed >_< -->
        <path d="M 52 42 L 44 47 L 52 52" fill="none" stroke="#D63031" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
      `;
      mouthSvg = `
        <path d="M 37 60 Q 40 56 43 60 Q 46 56 49 60" fill="none" stroke="#D63031" stroke-width="2.5" stroke-linecap="round" />
      `;
      extraAccents = `
        <!-- Angry sweat drops / conflict marks -->
        <path d="M 20 28 L 15 22" stroke="#FF7675" stroke-width="2.5" stroke-linecap="round" />
        <path d="M 60 28 L 65 22" stroke="#FF7675" stroke-width="2.5" stroke-linecap="round" />
        <!-- Red anger vein -->
        <path d="M 56 22 L 62 26 M 62 22 L 56 26" stroke="#D63031" stroke-width="2" stroke-linecap="round" />
      `;
      bodyFilter = 'filter: drop-shadow(0px 0px 8px rgba(235, 77, 75, 0.85));';
    } else if (state === 'testing') {
      // Puzzled / curious
      eyesSvg = `
        <circle cx="32" cy="46" r="4.5" fill="${b.eyeColor}" />
        <circle cx="34" cy="44" r="1.5" fill="#FFF" />
        <circle cx="48" cy="46" r="4.5" fill="${b.eyeColor}" />
        <circle cx="50" cy="44" r="1.5" fill="#FFF" />
      `;
      mouthSvg = `
        <circle cx="40" cy="58" r="2.5" fill="#E17055" />
      `;
      extraAccents = `
        <!-- Sweat droplet -->
        <path d="M 58 32 C 58 29, 61 28, 61 28 C 61 28, 64 29, 64 32 C 64 34, 62 36, 61 36 C 60 36, 58 34, 58 32 Z" fill="#74B9FF" />
      `;
    } else if (state === 'crowned') {
      // Solved & Victorious! Sparkly happy eyes + sparkling crown
      eyesSvg = `
        <!-- Happy closed arc eyes ^_^ -->
        <path d="M 28 48 Q 33 41 38 48" fill="none" stroke="#2D3436" stroke-width="3" stroke-linecap="round" />
        <path d="M 44 48 Q 49 41 54 48" fill="none" stroke="#2D3436" stroke-width="3" stroke-linecap="round" />
      `;
      mouthSvg = `
        <path d="M 36 57 Q 40 61 44 57" fill="none" stroke="#2D3436" stroke-width="2.5" stroke-linecap="round" />
      `;
      extraAccents = `
        <!-- Sparkly Royal Crown -->
        <path d="M 30 18 L 33 26 L 40 20 L 47 26 L 50 18 L 48 30 L 32 30 Z" fill="#FDCB6E" stroke="#E17055" stroke-width="1.5" stroke-linejoin="round" />
        <circle cx="40" cy="18" r="2.5" fill="#FF7675" />
        <circle cx="30" cy="17" r="1.5" fill="#6C5CE7" />
        <circle cx="50" cy="17" r="1.5" fill="#00B894" />
        <!-- Sparkles -->
        <text x="14" y="30" font-size="12" fill="#FDCB6E">✨</text>
        <text x="56" y="30" font-size="12" fill="#FDCB6E">✨</text>
      `;
      bodyFilter = 'filter: drop-shadow(0px 0px 8px rgba(253, 203, 110, 0.9));';
    } else {
      // Default: Cozy happy kitty
      eyesSvg = `
        <ellipse cx="32" cy="46" rx="4.5" ry="5.5" fill="${b.eyeColor}" />
        <circle cx="34" cy="44" r="1.8" fill="#FFF" />
        <ellipse cx="48" cy="46" rx="4.5" ry="5.5" fill="${b.eyeColor}" />
        <circle cx="50" cy="44" r="1.8" fill="#FFF" />
      `;
      mouthSvg = `
        <path d="M 36 56 Q 40 60 44 56 Q 48 60 52 56" fill="none" stroke="#2D3436" stroke-width="2" stroke-linecap="round" />
      `;
    }

    return `
      <svg viewBox="0 0 80 80" width="${size}" height="${size}" class="cat-svg transition-transform hover:scale-110 select-none pointer-events-none" style="${bodyFilter}">
        <defs>
          <linearGradient id="blushGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#FF7675" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#FF7675" stop-opacity="0"/>
          </linearGradient>
        </defs>

        <!-- Ears -->
        <polygon points="18,36 12,12 36,24" fill="${b.fur}" stroke="#2D3436" stroke-width="2" stroke-linejoin="round"/>
        <polygon points="20,32 16,17 32,24" fill="${b.innerEar}" />
        
        <polygon points="62,36 68,12 44,24" fill="${b.fur}" stroke="#2D3436" stroke-width="2" stroke-linejoin="round"/>
        <polygon points="60,32 64,17 48,24" fill="${b.innerEar}" />

        <!-- Head Base -->
        <ellipse cx="40" cy="48" rx="27" ry="23" fill="${b.fur}" stroke="#2D3436" stroke-width="2.5" />

        <!-- Breed Patch details -->
        ${b.patch !== b.fur ? `
          <path d="M 40 25 Q 52 25 56 38 Q 45 42 40 25 Z" fill="${b.patch}" opacity="0.85" />
          <path d="M 22 45 Q 16 54 26 62 Q 28 50 22 45 Z" fill="${b.darkPatch}" opacity="0.6" />
        ` : ''}

        <!-- Cheeks Blush -->
        <circle cx="23" cy="52" r="6" fill="#FF7675" opacity="0.45" />
        <circle cx="57" cy="52" r="6" fill="#FF7675" opacity="0.45" />

        <!-- Eyes -->
        ${eyesSvg}

        <!-- Cute Little Pink Nose -->
        <polygon points="38,52 42,52 40,55" fill="#FF7675" />

        <!-- Mouth -->
        ${mouthSvg}

        <!-- Whiskers -->
        <line x1="16" y1="48" x2="6" y2="46" stroke="#2D3436" stroke-width="1.8" stroke-linecap="round" />
        <line x1="15" y1="53" x2="6" y2="54" stroke="#2D3436" stroke-width="1.8" stroke-linecap="round" />
        <line x1="64" y1="48" x2="74" y2="46" stroke="#2D3436" stroke-width="1.8" stroke-linecap="round" />
        <line x1="65" y1="53" x2="74" y2="54" stroke="#2D3436" stroke-width="1.8" stroke-linecap="round" />

        <!-- Extra details (crown, sweat, anger mark) -->
        ${extraAccents}
      </svg>
    `;
  }
};

if (typeof window !== 'undefined') {
  window.CuteCats = CuteCats;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CuteCats;
}
