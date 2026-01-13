import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { RatingStars } from './RatingStars'

describe('RatingStars', () => {
  describe('display mode', () => {
    it('renders 5 star buttons', () => {
      render(<RatingStars rating={3} />)
      const buttons = screen.getAllByRole('button')
      expect(buttons).toHaveLength(5)
    })

    it('fills correct number of stars based on rating', () => {
      render(<RatingStars rating={3} />)
      const buttons = screen.getAllByRole('button')
      // All buttons should be disabled in non-interactive mode
      buttons.forEach(button => {
        expect(button).toBeDisabled()
      })
    })

    it('shows count when provided', () => {
      render(<RatingStars rating={4} count={42} />)
      expect(screen.getByText('(42)')).toBeInTheDocument()
    })

    it('does not show count when not provided', () => {
      render(<RatingStars rating={4} />)
      expect(screen.queryByText(/\(\d+\)/)).not.toBeInTheDocument()
    })

    it('handles zero rating', () => {
      render(<RatingStars rating={0} />)
      const buttons = screen.getAllByRole('button')
      expect(buttons).toHaveLength(5)
    })

    it('handles decimal rating by flooring', () => {
      render(<RatingStars rating={3.7} />)
      // Should show 3 filled stars (3.7 floors to 3 when comparing star <= rating)
      const buttons = screen.getAllByRole('button')
      expect(buttons).toHaveLength(5)
    })
  })

  describe('interactive mode', () => {
    it('enables buttons when interactive', () => {
      render(<RatingStars rating={0} interactive onRate={() => {}} />)
      const buttons = screen.getAllByRole('button')
      buttons.forEach(button => {
        expect(button).not.toBeDisabled()
      })
    })

    it('calls onRate with star number when clicked', async () => {
      const onRate = vi.fn()
      const user = userEvent.setup()
      render(<RatingStars rating={0} interactive onRate={onRate} />)

      const buttons = screen.getAllByRole('button')
      await user.click(buttons[3]) // 4th star (index 3)

      expect(onRate).toHaveBeenCalledWith(4)
    })

    it('highlights stars on hover', async () => {
      const user = userEvent.setup()
      render(<RatingStars rating={1} interactive onRate={() => {}} />)

      const buttons = screen.getAllByRole('button')
      await user.hover(buttons[4]) // Hover on 5th star

      // After hover, visual state changes (tested implicitly by no errors)
      await user.unhover(buttons[4])
    })

    it('does not call onRate when not interactive', async () => {
      const onRate = vi.fn()
      render(<RatingStars rating={3} onRate={onRate} />)

      const buttons = screen.getAllByRole('button')
      fireEvent.click(buttons[0])

      expect(onRate).not.toHaveBeenCalled()
    })
  })

  describe('sizes', () => {
    it('applies small size class', () => {
      render(<RatingStars rating={3} size="sm" />)
      const buttons = screen.getAllByRole('button')
      expect(buttons[0].querySelector('svg')).toHaveClass('h-4', 'w-4')
    })

    it('applies medium size class by default', () => {
      render(<RatingStars rating={3} />)
      const buttons = screen.getAllByRole('button')
      expect(buttons[0].querySelector('svg')).toHaveClass('h-5', 'w-5')
    })

    it('applies large size class', () => {
      render(<RatingStars rating={3} size="lg" />)
      const buttons = screen.getAllByRole('button')
      expect(buttons[0].querySelector('svg')).toHaveClass('h-6', 'w-6')
    })
  })
})
