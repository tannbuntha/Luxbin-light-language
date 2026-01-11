import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

interface CodeTranslationRequest {
    code: string;
    source_language: 'python' | 'javascript';
    target_language: 'python' | 'javascript';
    enable_type_inference?: boolean;
}

interface CodeTranslationResponse {
    success: boolean;
    original_code: string;
    translated_code: string;
    source_language: string;
    target_language: string;
    type_inference?: any;
    error?: string;
}

/**
 * POST /api/v1/translate-code
 * Translate code between programming languages
 */
export async function POST(request: NextRequest) {
    try {
        const body: CodeTranslationRequest = await request.json();

        const { code, source_language, target_language, enable_type_inference = false } = body;

        // Validate input
        if (!code || typeof code !== 'string') {
            return NextResponse.json({
                success: false,
                error: 'Code is required and must be a string'
            }, { status: 400 });
        }

        if (!['python', 'javascript'].includes(source_language)) {
            return NextResponse.json({
                success: false,
                error: 'Source language must be "python" or "javascript"'
            }, { status: 400 });
        }

        if (!['python', 'javascript'].includes(target_language)) {
            return NextResponse.json({
                success: false,
                error: 'Target language must be "python" or "javascript"'
            }, { status: 400 });
        }

        if (source_language === target_language) {
            return NextResponse.json({
                success: false,
                error: 'Source and target languages must be different'
            }, { status: 400 });
        }

        // Run Python translation script
        const translatedCode = await runPythonTranslator(code, source_language, target_language);

        // Optional type inference
        let typeInference = null;
        if (enable_type_inference) {
            try {
                typeInference = await runTypeInference(code, source_language);
            } catch (error) {
                console.warn('Type inference failed:', error);
            }
        }

        const response: CodeTranslationResponse = {
            success: true,
            original_code: code,
            translated_code: translatedCode,
            source_language,
            target_language,
            type_inference: typeInference
        };

        return NextResponse.json(response, { status: 200 });

    } catch (error) {
        console.error('Code translation error:', error);
        return NextResponse.json({
            success: false,
            error: error instanceof Error ? error.message : 'Internal server error'
        }, { status: 500 });
    }
}

/**
 * GET /api/v1/translate-code
 * Get information about supported languages and features
 */
export async function GET() {
    return NextResponse.json({
        service: 'LUXBIN Code Language Translator',
        version: '1.0.0',
        supported_languages: ['python', 'javascript'],
        supported_translations: [
            'python → javascript',
            'javascript → python'
        ],
        features: [
            'AST-based parsing',
            'Type inference (optional)',
            'Cross-language type mapping',
            'Error handling and validation'
        ],
        endpoints: {
            POST: '/api/v1/translate-code - Translate code between languages',
            GET: '/api/v1/translate-code - Get service information'
        }
    });
}

/**
 * Run Python code translator script
 */
async function runPythonTranslator(
    code: string,
    sourceLang: string,
    targetLang: string
): Promise<string> {
    return new Promise((resolve, reject) => {
        const pythonScript = path.join(process.cwd(), 'luxbin_code_translator.py');
        const pythonProcess = spawn('python3', [pythonScript], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        // Prepare command for the Python script
        const command = JSON.stringify({
            action: 'translate',
            code,
            source_language: sourceLang,
            target_language: targetLang
        }) + '\n';

        let output = '';
        let errorOutput = '';

        pythonProcess.stdout.on('data', (data) => {
            output += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`Python script failed: ${errorOutput}`));
                return;
            }

            try {
                const result = JSON.parse(output.trim());
                if (result.error) {
                    reject(new Error(result.error));
                } else {
                    resolve(result.translated_code);
                }
            } catch (e) {
                reject(new Error(`Failed to parse Python output: ${output}`));
            }
        });

        pythonProcess.on('error', (error) => {
            reject(new Error(`Failed to start Python process: ${error.message}`));
        });

        // Send command to Python script
        pythonProcess.stdin.write(command);
        pythonProcess.stdin.end();
    });
}

/**
 * Run type inference on code
 */
async function runTypeInference(code: string, language: string): Promise<any> {
    return new Promise((resolve, reject) => {
        const pythonScript = path.join(process.cwd(), 'luxbin_code_translator.py');
        const pythonProcess = spawn('python3', [pythonScript], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        const command = JSON.stringify({
            action: 'infer_types',
            code,
            language
        }) + '\n';

        let output = '';
        let errorOutput = '';

        pythonProcess.stdout.on('data', (data) => {
            output += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`Type inference failed: ${errorOutput}`));
                return;
            }

            try {
                const result = JSON.parse(output.trim());
                resolve(result);
            } catch (e) {
                reject(new Error(`Failed to parse type inference output: ${output}`));
            }
        });

        pythonProcess.on('error', (error) => {
            reject(new Error(`Failed to start Python process: ${error.message}`));
        });

        pythonProcess.stdin.write(command);
        pythonProcess.stdin.end();
    });
}