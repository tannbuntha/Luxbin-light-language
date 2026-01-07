'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Validator {
  name: string;
  location: string;
  qubits: number;
  queue: number;
  status: string;
  lastValidation: string;
}

interface ConsensusValidator {
  backend: string;
  vote: string;
  jobId: string;
}

interface LatestBlock {
  number: number;
  hash: string;
  quantumNonce: number;
  timestamp: string;
  transactions: number;
  miningBackend: string;
  jobId: string;
  consensusVotes: {
    total: number;
    valid: number;
    validators: ConsensusValidator[];
  };
}

interface BlockchainStatus {
  network: {
    status: string;
    validators: Validator[];
    totalValidators: number;
    consensusThreshold: number;
  };
  blockchain: {
    latestBlock: LatestBlock;
    totalBlocks: number;
    totalTransactions: number;
    pendingTransactions: number;
  };
  quantum: {
    activeJobs: number;
    completedJobs: number;
    totalQubitsAvailable: number;
    luxbinEncoding: boolean;
    photomicCommunication: string;
  };
  timestamp: string;
}

export default function QuantumBlockchainDashboard() {
  const [status, setStatus] = useState<BlockchainStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Fetch blockchain status
  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/quantum-blockchain/status', {
        cache: 'no-store'
      });

      if (!response.ok) {
        throw new Error('Failed to fetch blockchain status');
      }

      const data = await response.json();
      setStatus(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Real-time polling (every 5 seconds)
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Connecting to quantum network...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500 rounded-lg p-6">
        <h3 className="text-red-500 font-semibold mb-2">Connection Error</h3>
        <p className="text-gray-300">{error}</p>
      </div>
    );
  }

  if (!status) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Quantum Blockchain Network
          </h2>
          <p className="text-gray-400 mt-1">
            Real-time data from {status.network.totalValidators} quantum computers
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-400">
            Live • Updated {new Date(lastUpdate).toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Network Status */}
      <Card className="bg-black/40 border-blue-500/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">🌐</span>
            Network Status
          </CardTitle>
          <CardDescription>Distributed quantum consensus network</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-400">Status</p>
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                {status.network.status.toUpperCase()}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-gray-400">Validators</p>
              <p className="text-2xl font-bold text-white">{status.network.totalValidators}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Consensus</p>
              <p className="text-2xl font-bold text-white">
                {status.network.consensusThreshold}/{status.network.totalValidators}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Total Qubits</p>
              <p className="text-2xl font-bold text-purple-400">{status.quantum.totalQubitsAvailable}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quantum Validators */}
      <Card className="bg-black/40 border-purple-500/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">⚛️</span>
            Quantum Validators
          </CardTitle>
          <CardDescription>IBM Quantum computers running LUXBIN Chain</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {status.network.validators.map((validator) => (
              <div
                key={validator.name}
                className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 border border-blue-500/20 rounded-lg p-4"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-white">{validator.name}</h3>
                  <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-xs">
                    {validator.status}
                  </Badge>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Qubits:</span>
                    <span className="text-purple-400 font-semibold">{validator.qubits}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Queue:</span>
                    <span className="text-blue-400 font-semibold">{validator.queue}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Location:</span>
                    <span className="text-gray-400">{validator.location.split(',')[0]}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Latest Block */}
      <Card className="bg-black/40 border-green-500/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">🔗</span>
            Latest Block
          </CardTitle>
          <CardDescription>Most recent quantum-mined block</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-400">Block Number</p>
                <p className="text-2xl font-bold text-white">#{status.blockchain.latestBlock.number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Quantum Nonce</p>
                <p className="text-2xl font-bold text-purple-400">{status.blockchain.latestBlock.quantumNonce}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Transactions</p>
                <p className="text-2xl font-bold text-blue-400">{status.blockchain.latestBlock.transactions}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Mined By</p>
                <p className="text-sm font-semibold text-green-400">{status.blockchain.latestBlock.miningBackend.toUpperCase()}</p>
              </div>
            </div>

            <div className="bg-black/60 rounded-lg p-4 border border-gray-700">
              <p className="text-xs text-gray-400 mb-1">Block Hash</p>
              <p className="font-mono text-sm text-gray-300 break-all">{status.blockchain.latestBlock.hash}</p>
            </div>

            <div className="bg-black/60 rounded-lg p-4 border border-gray-700">
              <p className="text-xs text-gray-400 mb-2">Quantum Consensus</p>
              <div className="flex items-center gap-2 mb-3">
                <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                  ✓ {status.blockchain.latestBlock.consensusVotes.valid}/{status.blockchain.latestBlock.consensusVotes.total} Validators
                </Badge>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                {status.blockchain.latestBlock.consensusVotes.validators.map((v) => (
                  <div key={v.backend} className="flex items-center gap-2 text-xs">
                    <span className="text-green-400">✓</span>
                    <span className="text-gray-300">{v.backend.toUpperCase()}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-4 text-xs text-gray-400">
              <span>Job ID: {status.blockchain.latestBlock.jobId}</span>
              <span>•</span>
              <span>{new Date(status.blockchain.latestBlock.timestamp).toLocaleString()}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Blockchain Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-black/40 border-blue-500/30">
          <CardHeader>
            <CardTitle className="text-lg">Total Blocks</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-blue-400">{status.blockchain.totalBlocks}</p>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-purple-500/30">
          <CardHeader>
            <CardTitle className="text-lg">Total Transactions</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-purple-400">{status.blockchain.totalTransactions}</p>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-green-500/30">
          <CardHeader>
            <CardTitle className="text-lg">Quantum Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-green-400">{status.quantum.completedJobs}</p>
            <p className="text-sm text-gray-400 mt-1">{status.quantum.activeJobs} active</p>
          </CardContent>
        </Card>
      </div>

      {/* LUXBIN Encoding Status */}
      <Card className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 border-purple-500/30">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">LUXBIN Photonic Encoding</h3>
              <p className="text-sm text-gray-400">400-700nm wavelength quantum communication</p>
            </div>
            <div className="text-right">
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-lg px-4 py-2">
                {status.quantum.luxbinEncoding ? '✓ ACTIVE' : '○ INACTIVE'}
              </Badge>
              <p className="text-xs text-gray-400 mt-2">
                Photomic: {status.quantum.photomicCommunication}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
