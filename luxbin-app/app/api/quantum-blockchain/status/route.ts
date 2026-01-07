import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * API endpoint to get real-time quantum blockchain status
 * Returns current state from quantum computers
 *
 * Data Sources (in priority order):
 * 1. quantum_blockchain_status.json (real-time from Python service)
 * 2. Mock data (if file doesn't exist)
 */
export async function GET(request: NextRequest) {
  try {
    // Try to read from actual blockchain service data file
    const statusFilePath = path.join(process.cwd(), '..', 'quantum_blockchain_status.json');

    let blockchainStatus;

    try {
      // Check if real blockchain data exists
      if (fs.existsSync(statusFilePath)) {
        const fileContent = fs.readFileSync(statusFilePath, 'utf-8');
        blockchainStatus = JSON.parse(fileContent);
        console.log('✅ Reading REAL quantum blockchain data');
      } else {
        // Fall back to mock data if service isn't running
        console.log('⚠️  Using mock data (blockchain service not running)');
        blockchainStatus = getMockData();
      }
    } catch (fileError) {
      console.log('⚠️  Error reading blockchain file, using mock data:', fileError);
      blockchainStatus = getMockData();
    }

    return NextResponse.json(blockchainStatus, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });

  } catch (error) {
    console.error('Error fetching quantum blockchain status:', error);
    return NextResponse.json(
      { error: 'Failed to fetch blockchain status' },
      { status: 500 }
    );
  }
}

function getMockData() {
  return {
    network: {
      status: 'online',
      validators: [
        {
          name: 'ibm_fez',
          location: 'Yorktown Heights, NY',
          qubits: 156,
          queue: 0,
          status: 'active',
          lastValidation: new Date().toISOString()
        },
        {
          name: 'ibm_torino',
          location: 'Yorktown Heights, NY',
          qubits: 133,
          queue: 0,
          status: 'active',
          lastValidation: new Date().toISOString()
        },
        {
          name: 'ibm_marrakesh',
          location: 'Yorktown Heights, NY',
          qubits: 156,
          queue: 10866,
          status: 'active',
          lastValidation: new Date().toISOString()
        }
      ],
      totalValidators: 3,
      consensusThreshold: 2
    },
    blockchain: {
      latestBlock: {
        number: 1,
        hash: '86923cef9c40f3d1a07d7393bdf64b487aad3e8986d16eeaeb0b9a7ab6519f4b',
        quantumNonce: 255,
        timestamp: new Date().toISOString(),
        transactions: 1,
        miningBackend: 'ibm_fez',
        jobId: 'd5fdb5n67pic7382vro0',
        consensusVotes: {
          total: 3,
          valid: 3,
          validators: [
            { backend: 'ibm_fez', vote: 'valid', jobId: 'd5fdapcpe0pc73ajsing' },
            { backend: 'ibm_torino', vote: 'valid', jobId: 'd5fdb5n67pic7382vro0' },
            { backend: 'ibm_marrakesh', vote: 'valid', jobId: 'd5fdb7nea9qs738vo960' }
          ]
        }
      },
      totalBlocks: 1,
      totalTransactions: 1,
      pendingTransactions: 0
    },
    quantum: {
      activeJobs: 0,
      completedJobs: 3,
      totalQubitsAvailable: 445,
      luxbinEncoding: true,
      photomicCommunication: 'active'
    },
    timestamp: new Date().toISOString(),
    _mock: true  // Flag to indicate this is mock data
  };
}
