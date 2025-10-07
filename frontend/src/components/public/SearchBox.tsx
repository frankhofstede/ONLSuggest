/**
 * SearchBox Component
 * A prominently displayed search input field for Dutch municipal service queries.
 * Features:
 * - UTF-8 Dutch character support (ë, ï, ü, é, etc.)
 * - 2-character minimum validation with visual feedback
 * - Debounced query change callback (150ms)
 * - Keyboard navigation (Tab, Escape, Arrow Down)
 * - WCAG 2.1 AA accessibility attributes
 */
import { useState, useCallback, useMemo, KeyboardEvent, ChangeEvent } from 'react'
import { debounce } from '../../utils/debounce'

export interface SearchBoxProps {
  /** Callback fired when query changes and meets minimum character requirement (debounced) */
  onQueryChange: (query: string) => void
  /** Callback fired when Arrow Down key is pressed (for focusing first suggestion) */
  onArrowDown?: () => void
  /** Placeholder text for the input field */
  placeholder?: string
  /** Minimum number of characters required before triggering onQueryChange */
  minChars?: number
  /** Whether the suggestions dropdown is currently expanded */
  ariaExpanded?: boolean
  /** ID of the currently active suggestion (for aria-activedescendant) */
  activeDescendantId?: string
}

export function SearchBox({
  onQueryChange,
  onArrowDown,
  placeholder = 'Zoek naar gemeentediensten...',
  minChars = 2,
  ariaExpanded = false,
  activeDescendantId
}: SearchBoxProps) {
  const [query, setQuery] = useState('')
  const [isValid, setIsValid] = useState(false)

  // Debounced query change callback
  const debouncedOnQueryChange = useMemo(
    () => debounce(onQueryChange, 150),
    [onQueryChange]
  )

  // Handle input change
  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value
    setQuery(newQuery)

    // Validate query length
    const valid = newQuery.length >= minChars
    setIsValid(valid)

    // Only trigger callback if valid
    if (valid) {
      debouncedOnQueryChange(newQuery)
    }
  }, [minChars, debouncedOnQueryChange])

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLInputElement>) => {
    switch (e.key) {
      case 'Escape':
        // Clear input and reset validation
        setQuery('')
        setIsValid(false)
        e.preventDefault()
        break

      case 'ArrowDown':
        // Move focus to first suggestion (if callback provided)
        if (onArrowDown && isValid) {
          onArrowDown()
          e.preventDefault()
        }
        break

      // Tab is handled natively by browser, no action needed
    }
  }, [onArrowDown, isValid])

  // Determine border color based on validation state
  const getBorderColor = () => {
    if (query.length === 0) {
      return 'border-gray-300 focus:border-blue-500' // Neutral when empty
    }
    if (isValid) {
      return 'border-blue-500' // Valid: blue border
    }
    return 'border-red-500' // Invalid: red border
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <input
        type="text"
        value={query}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={`
          w-full px-6 py-4 text-lg
          border-2 rounded-lg
          transition-colors duration-200
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
          ${getBorderColor()}
        `}
        // WCAG 2.1 AA Accessibility attributes
        aria-label="Zoek naar gemeentediensten"
        role="combobox"
        aria-expanded={ariaExpanded}
        aria-controls={ariaExpanded ? 'suggestions-list' : undefined}
        aria-activedescendant={activeDescendantId}
        aria-autocomplete="list"
        tabIndex={0}
        autoComplete="off"
        spellCheck="false"
      />

      {/* Helper text for minimum character requirement */}
      {query.length > 0 && !isValid && (
        <p className="mt-2 text-sm text-red-600" role="alert" aria-live="polite">
          Typ minimaal {minChars} tekens
        </p>
      )}
    </div>
  )
}
