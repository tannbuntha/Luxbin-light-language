"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';

type WaveMode = 'photonic' | 'acoustic' | 'radio' | 'superposition';

interface WaveData {
  colors: string[];
  wavelengths: string[];
  frequencies: string[];
  amplitudes: number[][];
}

const LUXBIN_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?;:-()[]{}@#$%^&*+=_~`<>\"'|\\";

export function LuxbinMultiWaveTranslator() {
  const [inputText, setInputText] = useState('HELLO QUANTUM');
  const [currentMode, setCurrentMode] = useState<WaveMode>('photonic');
  const [naturalLang, setNaturalLang] = useState('Your input text will appear here');
  const [luxbinDict, setLuxbinDict] = useState('LUXBIN characters will appear here');
  const [binaryCode, setBinaryCode] = useState('Binary representation will appear here');
  const [wavelengthInfo, setWavelengthInfo] = useState('');
  const [frequencyInfo, setFrequencyInfo] = useState('');
  const [activeStep, setActiveStep] = useState<number | null>(null);
  const [waveColors, setWaveColors] = useState<string[]>([]);
  const [amplitudes, setAmplitudes] = useState<number[][]>([]);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const oscillatorsRef = useRef<OscillatorNode[]>([]);
  const animationRef = useRef<number | null>(null);

  // HSL to RGB conversion
  const hslToRgb = useCallback((h: number, s: number, l: number): [number, number, number] => {
    h /= 360;
    s /= 100;
    l /= 100;
    const hue2rgb = (p: number, q: number, t: number) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1/6) return p + (q - p) * 6 * t;
      if (t < 1/2) return q;
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
      return p;
    };
    let r, g, b;
    if (s === 0) {
      r = g = b = l;
    } else {
      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r = hue2rgb(p, q, h + 1/3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1/3);
    }
    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
  }, []);

  // Convert text to binary
  const textToBinary = useCallback((text: string): string => {
    return text.split('').map(char => {
      return char.charCodeAt(0).toString(2).padStart(8, '0');
    }).join(' ');
  }, []);

  // Convert binary to LUXBIN characters
  const binaryToLuxbin = useCallback((binary: string): string => {
    const cleanBinary = binary.replace(/\s/g, '');
    let result = '';
    for (let i = 0; i < cleanBinary.length; i += 6) {
      const chunk = cleanBinary.substr(i, 6).padEnd(6, '0');
      const index = parseInt(chunk, 2) % LUXBIN_ALPHABET.length;
      result += LUXBIN_ALPHABET[index];
    }
    return result;
  }, []);

  // Convert LUXBIN to multi-wave encoding
  const luxbinToWaves = useCallback((luxbin: string): WaveData => {
    const colors: string[] = [];
    const wavelengths: string[] = [];
    const frequencies: string[] = [];
    const amplitudes: number[][] = [];

    for (let i = 0; i < luxbin.length; i += 3) {
      const char1 = luxbin[i] || 'A';
      const char2 = luxbin[i + 1] || 'A';
      const char3 = luxbin[i + 2] || 'A';

      const index1 = LUXBIN_ALPHABET.indexOf(char1.toUpperCase());
      const index2 = LUXBIN_ALPHABET.indexOf(char2.toUpperCase());
      const index3 = LUXBIN_ALPHABET.indexOf(char3.toUpperCase());

      // Primary wavelength (visible light)
      const hue = (index1 / LUXBIN_ALPHABET.length) * 360;
      const rgb = hslToRgb(hue, 80, 60);
      colors.push(`rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`);
      wavelengths.push(`${Math.round(400 + (hue / 360) * 300)}nm`);

      // Secondary frequencies based on mode
      if (currentMode === 'acoustic') {
        const freq1 = 200 + (index1 / LUXBIN_ALPHABET.length) * 19980;
        frequencies.push(`${Math.round(freq1)}Hz`);
        amplitudes.push([0.3, 0.3, 0.3]);
      } else if (currentMode === 'radio') {
        const freq1 = 1000000 + (index1 / LUXBIN_ALPHABET.length) * 99000000;
        frequencies.push(`${(freq1/1000000).toFixed(1)}MHz`);
        amplitudes.push([0.3, 0.3, 0.3]);
      } else if (currentMode === 'superposition') {
        const baseFreq = 440 + (index1 / LUXBIN_ALPHABET.length) * 880;
        const freq1 = baseFreq;
        const freq2 = baseFreq * 1.25;
        const freq3 = baseFreq * 1.5;
        frequencies.push(`${Math.round(freq1)}Hz | ${Math.round(freq2)}Hz | ${Math.round(freq3)}Hz`);
        amplitudes.push([0.4, 0.4, 0.4]);
      }
    }

    return { colors, wavelengths, frequencies, amplitudes };
  }, [currentMode, hslToRgb]);

  // Draw waves on canvas
  const drawWaves = useCallback((colors: string[], amplitudes: number[][]) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const time = Date.now() * 0.005;
    const centerY = canvas.height / 2;

    colors.forEach((color, index) => {
      if (index >= 3) return;

      const amp = amplitudes[index] || [0.3, 0.3, 0.3];
      const yOffset = (index - 1) * 40;

      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();

      for (let x = 0; x < canvas.width; x++) {
        let y = 0;

        if (currentMode === 'superposition' && index === 0) {
          y += Math.sin(x * 0.02 + time) * amp[0] * 30;
          y += Math.sin(x * 0.025 + time * 1.25) * amp[1] * 30;
          y += Math.sin(x * 0.03 + time * 1.5) * amp[2] * 30;
        } else {
          y = Math.sin(x * 0.02 + time + index * Math.PI / 3) * amp[0] * 30;
        }

        if (x === 0) {
          ctx.moveTo(x, centerY + y + yOffset);
        } else {
          ctx.lineTo(x, centerY + y + yOffset);
        }
      }

      ctx.stroke();
    });
  }, [currentMode]);

  // Play audio
  const playAudio = useCallback(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }

    stopAudio();

    const binary = textToBinary(inputText);
    const luxbin = binaryToLuxbin(binary);
    const { frequencies, amplitudes } = luxbinToWaves(luxbin);

    frequencies.forEach((freqStr, index) => {
      if (currentMode === 'superposition' && index === 0) {
        const baseFreq = parseFloat(freqStr.split(' | ')[0]);
        const freqs = [baseFreq, baseFreq * 1.25, baseFreq * 1.5];

        freqs.forEach((freq, i) => {
          if (freq && freq > 0) {
            const oscillator = audioContextRef.current!.createOscillator();
            const gainNode = audioContextRef.current!.createGain();

            oscillator.frequency.setValueAtTime(freq, audioContextRef.current!.currentTime);
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(amplitudes[index][i] || 0.1, audioContextRef.current!.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContextRef.current!.currentTime + 2);

            oscillator.connect(gainNode);
            gainNode.connect(audioContextRef.current!.destination);

            oscillator.start();
            oscillator.stop(audioContextRef.current!.currentTime + 2);

            oscillatorsRef.current.push(oscillator);
          }
        });
      } else {
        const freq = parseFloat(freqStr.split('Hz')[0]);
        if (freq && freq > 0) {
          const oscillator = audioContextRef.current!.createOscillator();
          const gainNode = audioContextRef.current!.createGain();

          oscillator.frequency.setValueAtTime(freq, audioContextRef.current!.currentTime);
          oscillator.type = 'sine';

          gainNode.gain.setValueAtTime(0.1, audioContextRef.current!.currentTime);
          gainNode.gain.exponentialRampToValueAtTime(0.01, audioContextRef.current!.currentTime + 1);

          oscillator.connect(gainNode);
          gainNode.connect(audioContextRef.current!.destination);

          oscillator.start();
          oscillator.stop(audioContextRef.current!.currentTime + 1);

          oscillatorsRef.current.push(oscillator);
        }
      }
    });
  }, []);

  // Stop audio
  const stopAudio = useCallback(() => {
    oscillatorsRef.current.forEach(osc => {
      try {
        osc.stop();
      } catch (e) {
        // Already stopped
      }
    });
    oscillatorsRef.current = [];
  }, []);

  // Translate function
  const translate = useCallback(() => {
    if (!inputText.trim()) {
      alert('Please enter some text to translate!');
      return;
    }

    setActiveStep(null);

    // Step 1: Natural Language
    setNaturalLang(inputText);
    setActiveStep(1);

    setTimeout(() => {
      // Step 2: Binary Code
      const binary = textToBinary(inputText);
      setBinaryCode(binary);
      setActiveStep(2);

      setTimeout(() => {
        // Step 3: LUXBIN Dictionary
        const luxbin = binaryToLuxbin(binary);
        setLuxbinDict(luxbin);
        setActiveStep(3);

        setTimeout(() => {
          // Step 4: Multi-Wave Encoding
          const { colors, wavelengths, frequencies, amplitudes } = luxbinToWaves(luxbin);
          setWaveColors(colors);
          setAmplitudes(amplitudes);
          setWavelengthInfo(`Wavelengths: ${wavelengths.slice(0, 8).join(', ')}${wavelengths.length > 8 ? '...' : ''}`);

          if (frequencies.length > 0) {
            setFrequencyInfo(`Frequencies: ${frequencies.slice(0, 3).join(', ')}${frequencies.length > 3 ? '...' : ''}`);
          }

          setActiveStep(4);

          // Start animation
          if (animationRef.current) {
            cancelAnimationFrame(animationRef.current);
          }

          const animate = () => {
            drawWaves(colors, amplitudes);
            animationRef.current = requestAnimationFrame(animate);
          };
          animate();

        }, 1000);
      }, 1000);
    }, 1000);
  }, [inputText, textToBinary, binaryToLuxbin, luxbinToWaves, drawWaves]);

  // Generate light show using Python API
  const generateLightShow = useCallback(async () => {
    if (!inputText.trim()) {
      alert('Please enter some text first!');
      return;
    }

    try {
      // Call the Light Language API
      const response = await fetch('/api/v1/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: inputText,
          enable_quantum: true,
          format: 'full'
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();

      if (data.success && data.light_show) {
        // Extract colors and wavelengths from API response
        const colors = data.light_show.light_sequence.map((item: any) => {
          const wavelength = item.wavelength_nm;
          const hue = ((wavelength - 400) / 300) * 360;
          return `hsl(${hue.toFixed(0)}, 70%, 60%)`;
        });

        const amplitudes = data.light_show.light_sequence.map(() => [0.4, 0.4, 0.4]);

        setWaveColors(colors);
        setAmplitudes(amplitudes);
        setLuxbinDict(data.luxbin_representation);
        setBinaryCode(data.binary_code);
        setWavelengthInfo(`Wavelengths: ${data.light_show.light_sequence.slice(0, 8).map((s: any) => s.wavelength_nm.toFixed(1) + 'nm').join(', ')}`);

        if (animationRef.current) {
          cancelAnimationFrame(animationRef.current);
        }

        const animate = () => {
          drawWaves(colors, amplitudes);
          animationRef.current = requestAnimationFrame(animate);
        };
        animate();

        setActiveStep(4);

        if (currentMode !== 'photonic') {
          setTimeout(() => playAudio(), 500);
        }
      }
    } catch (error) {
      console.error('API Error:', error);
      // Fallback to local processing
      const binary = textToBinary(inputText);
      const luxbin = binaryToLuxbin(binary);
      const { colors, amplitudes } = luxbinToWaves(luxbin);

      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }

      const animate = () => {
        drawWaves(colors, amplitudes);
        animationRef.current = requestAnimationFrame(animate);
      };
      animate();

      setActiveStep(4);

      if (currentMode !== 'photonic') {
        setTimeout(() => playAudio(), 500);
      }
    }
  }, [inputText, currentMode, textToBinary, binaryToLuxbin, luxbinToWaves, drawWaves, playAudio]);

  // Clear all
  const clearAll = useCallback(() => {
    setInputText('');
    setNaturalLang('Your input text will appear here');
    setLuxbinDict('LUXBIN characters will appear here');
    setBinaryCode('Binary representation will appear here');
    setWavelengthInfo('');
    setFrequencyInfo('');
    setActiveStep(null);
    setWaveColors([]);

    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }

    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }

    stopAudio();
  }, [stopAudio]);

  // Initialize
  useEffect(() => {
    translate();
  }, []);

  // Cleanup
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      stopAudio();
    };
  }, [stopAudio]);

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl">
        <h1 className="text-center mb-4 bg-gradient-to-r from-orange-400 via-purple-500 to-cyan-400 bg-clip-text text-transparent text-4xl font-bold">
          🌈🎵 LUXBIN Multi-Wave Translator
        </h1>
        <p className="text-center text-gray-300 mb-8 text-lg">
          Advanced photonic communication with acoustic superposition and multi-wavelength encoding
        </p>

        <div className="mb-6">
          <label className="block text-white font-semibold mb-2">Enter Natural Language:</label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="w-full p-4 bg-white/90 text-gray-800 rounded-xl border-0 text-lg resize-none focus:ring-2 focus:ring-purple-500"
            rows={4}
            placeholder="Type your message here... e.g., 'Hello Quantum World'"
          />
        </div>

        <div className="flex flex-wrap justify-center gap-4 mb-6">
          <button
            onClick={() => setCurrentMode('photonic')}
            className={`px-6 py-3 rounded-full font-semibold transition-all ${
              currentMode === 'photonic' ? 'bg-cyan-500 text-white' : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            🌈 Photonic Only
          </button>
          <button
            onClick={() => setCurrentMode('acoustic')}
            className={`px-6 py-3 rounded-full font-semibold transition-all ${
              currentMode === 'acoustic' ? 'bg-cyan-500 text-white' : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            🎵 Acoustic Waves
          </button>
          <button
            onClick={() => setCurrentMode('radio')}
            className={`px-6 py-3 rounded-full font-semibold transition-all ${
              currentMode === 'radio' ? 'bg-cyan-500 text-white' : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            📻 Radio Waves
          </button>
          <button
            onClick={() => setCurrentMode('superposition')}
            className={`px-6 py-3 rounded-full font-semibold transition-all ${
              currentMode === 'superposition' ? 'bg-yellow-500 text-white' : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            ⚛️ Quantum Superposition
          </button>
        </div>

        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <button
            onClick={translate}
            className="bg-gradient-to-r from-orange-500 to-purple-600 text-white px-8 py-4 rounded-full font-bold text-lg hover:scale-105 transition-transform"
          >
            🔄 Translate to LUXBIN
          </button>
          <button
            onClick={generateLightShow}
            className="bg-gradient-to-r from-purple-500 to-cyan-500 text-white px-8 py-4 rounded-full font-bold text-lg hover:scale-105 transition-transform"
          >
            ✨ Generate Light Show
          </button>
          <button
            onClick={clearAll}
            className="bg-red-500/80 text-white px-8 py-4 rounded-full font-bold text-lg hover:bg-red-500 transition-colors"
          >
            🗑️ Clear
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className={`p-6 rounded-xl transition-all ${activeStep === 1 ? 'bg-cyan-500/20 border-2 border-cyan-400' : 'bg-white/10'}`}>
            <h3 className="text-xl font-bold text-orange-400 mb-4">📝 Natural Language</h3>
            <div className="bg-white/90 text-gray-800 p-4 rounded-lg text-sm font-mono min-h-[100px] overflow-y-auto">
              {naturalLang}
            </div>
          </div>

          <div className={`p-6 rounded-xl transition-all ${activeStep === 2 ? 'bg-cyan-500/20 border-2 border-cyan-400' : 'bg-white/10'}`}>
            <h3 className="text-xl font-bold text-orange-400 mb-4">📚 LUXBIN Dictionary</h3>
            <div className="bg-white/90 text-gray-800 p-4 rounded-lg text-sm font-mono min-h-[100px] overflow-y-auto">
              {luxbinDict}
            </div>
          </div>

          <div className={`p-6 rounded-xl transition-all ${activeStep === 3 ? 'bg-cyan-500/20 border-2 border-cyan-400' : 'bg-white/10'}`}>
            <h3 className="text-xl font-bold text-orange-400 mb-4">🔢 Binary Code</h3>
            <div className="bg-white/90 text-gray-800 p-4 rounded-lg text-sm font-mono min-h-[100px] overflow-y-auto whitespace-pre-wrap break-all">
              {binaryCode}
            </div>
          </div>

          <div className={`p-6 rounded-xl transition-all ${activeStep === 4 ? 'bg-cyan-500/20 border-2 border-cyan-400' : 'bg-white/10'}`}>
            <h3 className="text-xl font-bold text-orange-400 mb-4">🌈 Multi-Wave Encoding</h3>
            <div className="flex flex-wrap gap-2 mb-4">
              {waveColors.map((color, index) => (
                <div
                  key={index}
                  className="w-8 h-8 rounded-lg border-2 border-white/30 hover:scale-110 transition-transform"
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
            <div className="text-xs text-gray-300 mb-2">{wavelengthInfo}</div>
            <div className="text-xs text-gray-300">{frequencyInfo}</div>
            {(currentMode === 'acoustic' || currentMode === 'radio' || currentMode === 'superposition') && (
              <div className="flex gap-2 mt-4">
                <button onClick={playAudio} className="bg-green-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-600">
                  ▶️ Play Audio
                </button>
                <button onClick={stopAudio} className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-600">
                  ⏹️ Stop
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="bg-black/50 rounded-xl p-6 mb-6">
          <canvas
            ref={canvasRef}
            width={800}
            height={200}
            className="w-full h-48 bg-gradient-to-b from-gray-900 to-black rounded-lg"
          />
        </div>

        {currentMode === 'superposition' && (
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-6 mb-6">
            <h4 className="text-yellow-400 font-bold mb-2">⚛️ Quantum Superposition Analysis</h4>
            <p className="text-gray-300">
              Three wavelengths combined with matched amplitudes create quantum-like interference patterns for enhanced data density.
              The harmonic relationships (fundamental + perfect fifth + perfect octave) generate complex waveforms that can encode more information.
            </p>
          </div>
        )}

        <div className="text-center text-gray-400 text-sm">
          <p>Multi-modal communication: Photonic + Acoustic + Radio waves with quantum superposition | Powered by <a href="https://github.com/mermaidnicheboutique-code/luxbin-light-language" className="text-cyan-400 hover:underline">LUXBIN Light Language</a></p>
        </div>
      </div>
    </div>
  );
}