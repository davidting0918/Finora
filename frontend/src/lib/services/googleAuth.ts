/**
 * Google OAuth Authentication Service
 * Handles Google Identity Services integration for OAuth authentication
 */

import { getGoogleConfig } from '../api/config'

// Google Identity Services types
declare global {
  interface Window {
    google: any
    handleGoogleCallback: (response: CredentialResponse) => void
  }
}

export interface CredentialResponse {
  credential: string
  select_by: string
  clientId?: string
}

export interface GoogleAuthOptions {
  onSuccess: (credential: string) => void
  onError: (error: string) => void
}

export class GoogleAuthService {
  private isGoogleLoaded = false
  private googleConfig = getGoogleConfig()
  private currentOptions: GoogleAuthOptions | null = null

  /**
   * Initialize Google Identity Services
   * This should be called once when the app starts
   */
  public async initializeGoogle(): Promise<void> {
    return new Promise((resolve, reject) => {
      // Check if Google Identity Services is already loaded
      if (window.google) {
        this.isGoogleLoaded = true
        resolve()
        return
      }

      // Load Google Identity Services script
      const script = document.createElement('script')
      script.src = 'https://accounts.google.com/gsi/client'
      script.async = true
      script.defer = true

      script.onload = () => {
        this.isGoogleLoaded = true
        console.log('🔗 Google Identity Services loaded successfully')
        resolve()
      }

      script.onerror = () => {
        console.error('Failed to load Google Identity Services')
        reject(new Error('Failed to load Google Identity Services'))
      }

      document.head.appendChild(script)
    })
  }

  /**
   * Initialize Google Sign-In (simplified version)
   */
  public initializeGoogleSignIn(options: GoogleAuthOptions): void {
    if (!this.isGoogleLoaded) {
      throw new Error('Google Identity Services not loaded. Call initializeGoogle() first.')
    }

    // Store options for later use
    this.currentOptions = options

    console.log('✅ Google Sign-In initialized successfully (native buttons will handle their own callbacks)')
  }


  /**
   * Render Google Sign-In button in a specific element
   */
  public renderButton(elementId: string, options: GoogleAuthOptions): void {
    if (!this.isGoogleLoaded) {
      throw new Error('Google Identity Services not loaded. Call initializeGoogle() first.')
    }

    try {
      console.log('🎨 Rendering native Google button in element:', elementId)

      // Set up callback for this specific button
      const buttonCallback = (response: CredentialResponse) => {
        console.log('📨 Native button callback received:', {
          hasCredential: !!response.credential,
          selectBy: response.select_by
        })

        if (response.credential) {
          options.onSuccess(response.credential)
        } else {
          console.error('❌ No credential in native button response')
          options.onError('No credential received from Google')
        }
      }

      // Initialize with button-specific callback
      window.google.accounts.id.initialize({
        client_id: this.googleConfig.clientId,
        callback: buttonCallback,
      })

      // Render the native button
      window.google.accounts.id.renderButton(
        document.getElementById(elementId),
        {
          theme: 'outline',
          size: 'large',
          type: 'standard',
          text: 'continue_with',
          width: 400,
        }
      )

      console.log('✅ Native Google button rendered successfully')
    } catch (error) {
      console.error('❌ Error rendering native Google button:', error)
      options.onError('Failed to render Google Sign-In button')
    }
  }

  /**
   * Check if Google Identity Services is loaded
   */
  public isLoaded(): boolean {
    return this.isGoogleLoaded
  }

  /**
   * Get Google Client ID
   */
  public getClientId(): string {
    return this.googleConfig.clientId
  }
}

// Export singleton instance
export const googleAuthService = new GoogleAuthService()
export default googleAuthService
