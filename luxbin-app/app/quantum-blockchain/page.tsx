import QuantumBlockchainDashboard from '@/components/QuantumBlockchainDashboard';

export const metadata = {
  title: 'Quantum Blockchain | LUXBIN',
  description: 'Real-time quantum blockchain network powered by IBM quantum computers',
};

export default function QuantumBlockchainPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold mb-4">
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              LUXBIN Quantum Blockchain
            </span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            The world's first blockchain validated and mined on real quantum computers.
            Distributed across IBM's quantum network with LUXBIN photonic encoding.
          </p>
          <div className="flex items-center justify-center gap-4 mt-6">
            <div className="flex items-center gap-2 bg-black/40 px-4 py-2 rounded-full border border-blue-500/30">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-300">Live Network</span>
            </div>
            <div className="bg-black/40 px-4 py-2 rounded-full border border-purple-500/30">
              <span className="text-sm text-gray-300">⚛️ Quantum-Powered</span>
            </div>
            <div className="bg-black/40 px-4 py-2 rounded-full border border-green-500/30">
              <span className="text-sm text-gray-300">💎 LUXBIN Encoded</span>
            </div>
          </div>
        </div>

        {/* Dashboard */}
        <QuantumBlockchainDashboard />

        {/* Footer Info */}
        <div className="mt-12 text-center">
          <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/20 rounded-lg p-8 max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-white mb-4">How It Works</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
              <div>
                <div className="text-3xl mb-2">🔗</div>
                <h4 className="font-semibold text-white mb-2">Quantum Validation</h4>
                <p className="text-sm text-gray-400">
                  Transactions are encoded as LUXBIN wavelengths and validated across 3 IBM quantum computers
                </p>
              </div>
              <div>
                <div className="text-3xl mb-2">⛏️</div>
                <h4 className="font-semibold text-white mb-2">Quantum Mining</h4>
                <p className="text-sm text-gray-400">
                  Blocks are mined using true quantum randomness, generating provably random nonces
                </p>
              </div>
              <div>
                <div className="text-3xl mb-2">🌐</div>
                <h4 className="font-semibold text-white mb-2">Distributed Consensus</h4>
                <p className="text-sm text-gray-400">
                  Byzantine fault tolerance achieved through quantum state correlations across the network
                </p>
              </div>
            </div>
          </div>

          <div className="mt-8 text-sm text-gray-400">
            <p>Powered by IBM Quantum (FEZ, TORINO, MARRAKESH) • LUXBIN Light Language • Qiskit Runtime</p>
            <p className="mt-2">
              Data updates every 5 seconds • Real-time quantum job monitoring
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
