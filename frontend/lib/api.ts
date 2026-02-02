// API client for Aethel backend

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface VerifyRequest {
  code: string;
}

export interface VerifyResponse {
  status: 'PROVED' | 'FAILED' | 'ERROR';
  message: string;
  proof?: any;
  audit_trail?: string[];
}

export interface Example {
  name: string;
  code: string;
  description: string;
}

export async function verifyCode(code: string): Promise<VerifyResponse> {
  try {
    const response = await fetch(`${API_URL}/api/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Verification error:', error);
    return {
      status: 'ERROR',
      message: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
}

export async function getExamples(): Promise<Example[]> {
  try {
    const response = await fetch(`${API_URL}/api/examples`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch examples:', error);
    return [];
  }
}

export async function compileCode(code: string): Promise<any> {
  try {
    const response = await fetch(`${API_URL}/api/compile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Compilation error:', error);
    throw error;
  }
}
