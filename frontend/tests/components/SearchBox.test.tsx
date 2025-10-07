/**
 * Unit tests for SearchBox component
 * Tests: UTF-8 input, validation, visual feedback, debouncing, keyboard navigation
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SearchBox } from '../../src/components/public/SearchBox'

describe('SearchBox', () => {
  let mockOnQueryChange: ReturnType<typeof vi.fn>
  let mockOnArrowDown: ReturnType<typeof vi.fn>

  beforeEach(() => {
    mockOnQueryChange = vi.fn()
    mockOnArrowDown = vi.fn()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
  })

  describe('UTF-8 Character Input', () => {
    it('should accept Dutch special characters (ë, ï, ü, é)', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'parkë')

      expect(input).toHaveValue('parkë')
    })

    it('should accept mixed Dutch characters', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'François büro')

      expect(input).toHaveValue('François büro')
    })
  })

  describe('2-Character Minimum Validation', () => {
    it('should NOT call onQueryChange when typing only 1 character', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'p')

      // Wait for debounce
      vi.advanceTimersByTime(200)

      expect(mockOnQueryChange).not.toHaveBeenCalled()
    })

    it('should call onQueryChange when typing 2 characters', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'pa')

      // Wait for debounce
      vi.advanceTimersByTime(200)

      expect(mockOnQueryChange).toHaveBeenCalledWith('pa')
    })

    it('should call onQueryChange when typing 3+ characters', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'park')

      // Wait for debounce
      vi.advanceTimersByTime(200)

      expect(mockOnQueryChange).toHaveBeenCalledWith('park')
    })

    it('should respect custom minChars prop', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} minChars={3} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'pa')

      // Wait for debounce
      vi.advanceTimersByTime(200)

      expect(mockOnQueryChange).not.toHaveBeenCalled()

      await user.type(input, 'r')
      vi.advanceTimersByTime(200)

      expect(mockOnQueryChange).toHaveBeenCalledWith('par')
    })
  })

  describe('Visual Feedback', () => {
    it('should show red border when 1 character is typed', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'p')

      expect(input).toHaveClass('border-red-500')
    })

    it('should show blue border when 2+ characters are typed', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'pa')

      expect(input).toHaveClass('border-blue-500')
    })

    it('should show helper text "Typ minimaal 2 tekens" when invalid', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'p')

      expect(screen.getByText('Typ minimaal 2 tekens')).toBeInTheDocument()
    })

    it('should hide helper text when valid', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'pa')

      expect(screen.queryByText('Typ minimaal 2 tekens')).not.toBeInTheDocument()
    })

    it('should not show helper text when input is empty', () => {
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      expect(screen.queryByText('Typ minimaal 2 tekens')).not.toBeInTheDocument()
    })
  })

  describe('Debouncing', () => {
    it('should debounce onQueryChange calls (150ms)', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')

      // Type quickly
      await user.type(input, 'park')

      // Should not be called yet
      expect(mockOnQueryChange).not.toHaveBeenCalled()

      // Advance timers by 150ms
      vi.advanceTimersByTime(150)

      // Should be called once with final value
      expect(mockOnQueryChange).toHaveBeenCalledTimes(1)
      expect(mockOnQueryChange).toHaveBeenCalledWith('park')
    })

    it('should only call onQueryChange once when typing quickly', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')

      // Type multiple characters quickly
      await user.type(input, 'parkeervergunning')

      // Advance through debounce
      vi.advanceTimersByTime(200)

      // Should only be called once with final value
      expect(mockOnQueryChange).toHaveBeenCalledTimes(1)
      expect(mockOnQueryChange).toHaveBeenCalledWith('parkeervergunning')
    })
  })

  describe('Keyboard Navigation', () => {
    it('should clear input when Escape is pressed', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'park')

      expect(input).toHaveValue('park')

      await user.keyboard('{Escape}')

      expect(input).toHaveValue('')
    })

    it('should call onArrowDown when Arrow Down is pressed and input is valid', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} onArrowDown={mockOnArrowDown} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'park')

      await user.keyboard('{ArrowDown}')

      expect(mockOnArrowDown).toHaveBeenCalledTimes(1)
    })

    it('should NOT call onArrowDown when input is invalid (< 2 chars)', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} onArrowDown={mockOnArrowDown} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'p')

      await user.keyboard('{ArrowDown}')

      expect(mockOnArrowDown).not.toHaveBeenCalled()
    })

    it('should be focusable with Tab key', () => {
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      expect(input).toHaveAttribute('tabIndex', '0')
    })
  })

  describe('Accessibility (WCAG 2.1 AA)', () => {
    it('should have aria-label', () => {
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      expect(input).toHaveAttribute('aria-label', 'Zoek naar gemeentediensten')
    })

    it('should have role="combobox"', () => {
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      expect(input).toBeInTheDocument()
    })

    it('should have aria-expanded attribute', () => {
      render(<SearchBox onQueryChange={mockOnQueryChange} ariaExpanded={false} />)

      const input = screen.getByRole('combobox')
      expect(input).toHaveAttribute('aria-expanded', 'false')
    })

    it('should update aria-expanded when prop changes', () => {
      const { rerender } = render(<SearchBox onQueryChange={mockOnQueryChange} ariaExpanded={false} />)

      let input = screen.getByRole('combobox')
      expect(input).toHaveAttribute('aria-expanded', 'false')

      rerender(<SearchBox onQueryChange={mockOnQueryChange} ariaExpanded={true} />)

      input = screen.getByRole('combobox')
      expect(input).toHaveAttribute('aria-expanded', 'true')
    })

    it('should have aria-activedescendant when provided', () => {
      render(<SearchBox onQueryChange={mockOnQueryChange} activeDescendantId="suggestion-1" />)

      const input = screen.getByRole('combobox')
      expect(input).toHaveAttribute('aria-activedescendant', 'suggestion-1')
    })

    it('should have aria-autocomplete="list"', () => {
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      expect(input).toHaveAttribute('aria-autocomplete', 'list')
    })

    it('should have helper text with role="alert" and aria-live="polite"', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBox onQueryChange={mockOnQueryChange} />)

      const input = screen.getByRole('combobox')
      await user.type(input, 'p')

      const helperText = screen.getByText('Typ minimaal 2 tekens')
      expect(helperText).toHaveAttribute('role', 'alert')
      expect(helperText).toHaveAttribute('aria-live', 'polite')
    })
  })
})
