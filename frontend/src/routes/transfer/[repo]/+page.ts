import type { PageLoad } from './$types'

function extractRepoUrlFromUrl(url: string): string | undefined {
  const match = url.match(/repo_url=([^&]+)/)
  if (match) {
    return decodeURIComponent(match[1])
  } else {
    return undefined
  }
}

function getLastSegmentFromUrl(url: string): string | null {
  try {
    const urlObject = new URL(url)
    const pathname = urlObject.pathname
    const segments = pathname.split('/')
    return segments[segments.length - 1] || null
  } catch (error: unknown) {
    console.error((error as Error).message)
    return null
  }
}

export const load: PageLoad = ({ params }) => {
  const url = params.repo
  const repoUrl = extractRepoUrlFromUrl(url)
  if (repoUrl) {
    const lastSegment = getLastSegmentFromUrl(repoUrl)
    console.log(`lastSegment or repo url: ${lastSegment}`)
    return {
      repo: lastSegment
    }
  } else {
    return {
      repo: 'error'
    }
  }
}
