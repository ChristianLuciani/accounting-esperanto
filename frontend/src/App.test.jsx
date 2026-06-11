import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from './App';

function mockFetch(impl) {
  global.fetch = vi.fn(impl);
}

describe('Kontablo dashboard', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders the title and the illustrative-data banner', async () => {
    mockFetch(async (url) => {
      if (url.endsWith('/health')) return { ok: true };
      if (url.endsWith('/accounts')) return { ok: true, json: async () => ({ total: 30 }) };
      return { ok: false };
    });
    render(<App />);
    expect(screen.getByText('kontablo')).toBeInTheDocument();
    // Honesty banner must be present and label samples as illustrative.
    expect(screen.getByRole('note')).toHaveTextContent(/illustrative samples/i);
    expect(screen.getByText(/Account Mapping \(illustrative\)/i)).toBeInTheDocument();
  });

  it('shows live ontology node count and Healthy status when API is up', async () => {
    mockFetch(async (url) => {
      if (url.endsWith('/health')) return { ok: true };
      if (url.endsWith('/accounts')) return { ok: true, json: async () => ({ total: 30 }) };
      return { ok: false };
    });
    render(<App />);
    await waitFor(() => expect(screen.getByText('Healthy')).toBeInTheDocument());
    expect(screen.getByText('30')).toBeInTheDocument();
  });

  it('degrades gracefully to Offline when the API is unreachable', async () => {
    mockFetch(async () => {
      throw new Error('network down');
    });
    render(<App />);
    await waitFor(() => expect(screen.getByText('Offline')).toBeInTheDocument());
    // No fabricated coverage/entity numbers leak into the UI.
    expect(screen.queryByText('94.2%')).not.toBeInTheDocument();
    expect(screen.getByRole('note')).toHaveTextContent(/API is currently unreachable/i);
  });

  it('does not display fabricated precise coverage metrics anywhere', async () => {
    mockFetch(async (url) => {
      if (url.endsWith('/health')) return { ok: true };
      if (url.endsWith('/accounts')) return { ok: true, json: async () => ({ total: 30 }) };
      return { ok: false };
    });
    const { container } = render(<App />);
    await waitFor(() => expect(screen.getByText('Healthy')).toBeInTheDocument());
    // The old hardcoded "Coverage 94.2% / Entities 12" must be gone.
    expect(container.textContent).not.toMatch(/94\.2%/);
  });
});
