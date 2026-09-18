import { render, screen } from '@testing-library/vue';
import { describe, expect, it } from 'vitest';

import App from './App.vue';

describe('App', () => {
  it('renders the project title', () => {
    render(App);

    expect(screen.getByRole('heading', { name: 'Device diagnostics' })).toBeInTheDocument();
  });

  it('shows the initial health state', () => {
    render(App);

    expect(screen.getByText('Health: checking')).toBeInTheDocument();
  });
});
