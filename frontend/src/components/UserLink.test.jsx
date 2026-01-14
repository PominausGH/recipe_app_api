import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { UserLink } from "./UserLink";

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe("UserLink", () => {
  const mockUser = {
    id: 1,
    name: "John Doe",
    profile_photo: null,
    is_verified: false,
  };

  it("renders nothing when user is null", () => {
    const { container } = renderWithRouter(<UserLink user={null} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders user name", () => {
    renderWithRouter(<UserLink user={mockUser} />);
    expect(screen.getByText("John Doe")).toBeInTheDocument();
  });

  it("renders link to user profile", () => {
    renderWithRouter(<UserLink user={mockUser} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/users/1");
  });

  it("renders initial when no profile photo", () => {
    renderWithRouter(<UserLink user={mockUser} />);
    expect(screen.getByText("J")).toBeInTheDocument();
  });

  it("renders profile photo when provided", () => {
    const userWithPhoto = { ...mockUser, profile_photo: "/photo.jpg" };
    renderWithRouter(<UserLink user={userWithPhoto} />);
    const img = screen.getByRole("img", { name: "John Doe" });
    expect(img).toHaveAttribute("src", "/photo.jpg");
  });

  it("hides photo when showPhoto is false", () => {
    renderWithRouter(<UserLink user={mockUser} showPhoto={false} />);
    expect(screen.queryByText("J")).not.toBeInTheDocument();
  });

  it("shows verified badge for verified users", () => {
    const verifiedUser = { ...mockUser, is_verified: true };
    renderWithRouter(<UserLink user={verifiedUser} />);
    expect(screen.getByText("(verified)")).toBeInTheDocument();
  });

  it("does not show verified badge for unverified users", () => {
    renderWithRouter(<UserLink user={mockUser} />);
    expect(screen.queryByText("(verified)")).not.toBeInTheDocument();
  });

  describe("disableLink prop", () => {
    it("renders as span instead of link when disableLink is true", () => {
      renderWithRouter(<UserLink user={mockUser} disableLink />);
      expect(screen.queryByRole("link")).not.toBeInTheDocument();
      expect(screen.getByText("John Doe")).toBeInTheDocument();
    });

    it("still renders user content when disableLink is true", () => {
      const verifiedUser = { ...mockUser, is_verified: true };
      renderWithRouter(<UserLink user={verifiedUser} disableLink />);
      expect(screen.getByText("John Doe")).toBeInTheDocument();
      expect(screen.getByText("(verified)")).toBeInTheDocument();
    });

    it("renders as link by default", () => {
      renderWithRouter(<UserLink user={mockUser} />);
      expect(screen.getByRole("link")).toBeInTheDocument();
    });
  });
});
