import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { FollowButton } from "./FollowButton";

const mockNavigate = vi.fn();
const mockMutateAsync = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock("../hooks/useAuth", () => ({
  useAuth: vi.fn(() => ({ isAuthenticated: true })),
}));

vi.mock("../hooks/useUsers", () => ({
  useFollowUser: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
}));

import { useAuth } from "../hooks/useAuth";
import { useFollowUser } from "../hooks/useUsers";

const renderFollowButton = (props = {}) => {
  return render(
    <BrowserRouter>
      <FollowButton userId={1} {...props} />
    </BrowserRouter>,
  );
};

describe("FollowButton", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuth.mockReturnValue({ isAuthenticated: true });
    useFollowUser.mockReturnValue({
      mutateAsync: mockMutateAsync,
      isPending: false,
    });
  });

  describe("initial state rendering", () => {
    it('renders "Follow" for not_following state', () => {
      renderFollowButton({ initialState: "not_following" });
      expect(
        screen.getByRole("button", { name: "Follow" }),
      ).toBeInTheDocument();
    });

    it('renders "Request" for not_following state when account is private', () => {
      renderFollowButton({ initialState: "not_following", isPrivate: true });
      expect(
        screen.getByRole("button", { name: "Request" }),
      ).toBeInTheDocument();
    });

    it('renders "Following" for following state', () => {
      renderFollowButton({ initialState: "following" });
      expect(
        screen.getByRole("button", { name: "Following" }),
      ).toBeInTheDocument();
    });

    it('renders "Requested" for requested state', () => {
      renderFollowButton({ initialState: "requested" });
      expect(
        screen.getByRole("button", { name: "Requested" }),
      ).toBeInTheDocument();
    });
  });

  describe("hover behavior", () => {
    it('shows "Unfollow" on hover when following', async () => {
      const user = userEvent.setup();
      renderFollowButton({ initialState: "following" });

      const button = screen.getByRole("button", { name: "Following" });
      await user.hover(button);

      expect(
        screen.getByRole("button", { name: "Unfollow" }),
      ).toBeInTheDocument();
    });

    it('reverts to "Following" when mouse leaves', async () => {
      const user = userEvent.setup();
      renderFollowButton({ initialState: "following" });

      const button = screen.getByRole("button", { name: "Following" });
      await user.hover(button);
      await user.unhover(button);

      expect(
        screen.getByRole("button", { name: "Following" }),
      ).toBeInTheDocument();
    });
  });

  describe("authentication", () => {
    it("redirects to login when not authenticated", async () => {
      useAuth.mockReturnValue({ isAuthenticated: false });
      const user = userEvent.setup();
      renderFollowButton();

      await user.click(screen.getByRole("button", { name: "Follow" }));

      expect(mockNavigate).toHaveBeenCalledWith("/login");
      expect(mockMutateAsync).not.toHaveBeenCalled();
    });

    it("does not redirect when authenticated", async () => {
      mockMutateAsync.mockResolvedValue({ status: "followed" });
      const user = userEvent.setup();
      renderFollowButton();

      await user.click(screen.getByRole("button", { name: "Follow" }));

      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe("follow actions", () => {
    it("calls mutateAsync with userId on click", async () => {
      mockMutateAsync.mockResolvedValue({ status: "followed" });
      const user = userEvent.setup();
      renderFollowButton({ userId: 42 });

      await user.click(screen.getByRole("button", { name: "Follow" }));

      expect(mockMutateAsync).toHaveBeenCalledWith(42);
    });

    it('updates to "following" state after successful follow', async () => {
      mockMutateAsync.mockResolvedValue({ status: "followed" });
      renderFollowButton();

      fireEvent.click(screen.getByRole("button", { name: "Follow" }));

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /Following|Unfollow/ }),
        ).toBeInTheDocument();
      });
    });

    it('updates to "requested" state for pending follow request', async () => {
      mockMutateAsync.mockResolvedValue({ status: "pending" });
      const user = userEvent.setup();
      renderFollowButton({ isPrivate: true });

      await user.click(screen.getByRole("button", { name: "Request" }));

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: "Requested" }),
        ).toBeInTheDocument();
      });
    });

    it('updates to "not_following" state after unfollow', async () => {
      mockMutateAsync.mockResolvedValue({ status: "unfollowed" });
      const user = userEvent.setup();
      renderFollowButton({ initialState: "following" });

      await user.click(screen.getByRole("button", { name: "Following" }));

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: "Follow" }),
        ).toBeInTheDocument();
      });
    });

    it('handles "removed from followers" status', async () => {
      mockMutateAsync.mockResolvedValue({ status: "removed from followers" });
      const user = userEvent.setup();
      renderFollowButton({ initialState: "following" });

      await user.click(screen.getByRole("button", { name: "Following" }));

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: "Follow" }),
        ).toBeInTheDocument();
      });
    });
  });

  describe("callbacks", () => {
    it("calls onStateChange with new state after follow", async () => {
      mockMutateAsync.mockResolvedValue({ status: "followed" });
      const onStateChange = vi.fn();
      const user = userEvent.setup();
      renderFollowButton({ onStateChange });

      await user.click(screen.getByRole("button", { name: "Follow" }));

      await waitFor(() => {
        expect(onStateChange).toHaveBeenCalledWith("following");
      });
    });

    it('calls onStateChange with "requested" for pending', async () => {
      mockMutateAsync.mockResolvedValue({ status: "pending" });
      const onStateChange = vi.fn();
      const user = userEvent.setup();
      renderFollowButton({ onStateChange, isPrivate: true });

      await user.click(screen.getByRole("button", { name: "Request" }));

      await waitFor(() => {
        expect(onStateChange).toHaveBeenCalledWith("requested");
      });
    });
  });

  describe("loading state", () => {
    it('shows "Loading..." when mutation is pending', () => {
      useFollowUser.mockReturnValue({
        mutateAsync: mockMutateAsync,
        isPending: true,
      });
      renderFollowButton();

      expect(
        screen.getByRole("button", { name: "Loading..." }),
      ).toBeInTheDocument();
    });

    it("disables button when mutation is pending", () => {
      useFollowUser.mockReturnValue({
        mutateAsync: mockMutateAsync,
        isPending: true,
      });
      renderFollowButton();

      expect(screen.getByRole("button")).toBeDisabled();
    });
  });

  describe("error handling", () => {
    it("shows error message when mutation fails", async () => {
      mockMutateAsync.mockRejectedValue(new Error("Network error"));
      const user = userEvent.setup();
      renderFollowButton();

      await user.click(screen.getByRole("button", { name: "Follow" }));

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: "Failed. Try again." }),
        ).toBeInTheDocument();
      });
    });

    it("clears error after 3 seconds", async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true });
      mockMutateAsync.mockRejectedValue(new Error("Network error"));
      renderFollowButton();

      fireEvent.click(screen.getByRole("button", { name: "Follow" }));

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: "Failed. Try again." }),
        ).toBeInTheDocument();
      });

      await vi.advanceTimersByTimeAsync(3000);

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: "Follow" }),
        ).toBeInTheDocument();
      });

      vi.useRealTimers();
    });
  });

  describe("state sync with initialState prop", () => {
    it("updates when initialState prop changes", () => {
      const { rerender } = renderFollowButton({
        initialState: "not_following",
      });
      expect(
        screen.getByRole("button", { name: "Follow" }),
      ).toBeInTheDocument();

      rerender(
        <BrowserRouter>
          <FollowButton userId={1} initialState="following" />
        </BrowserRouter>,
      );

      expect(
        screen.getByRole("button", { name: "Following" }),
      ).toBeInTheDocument();
    });
  });
});
