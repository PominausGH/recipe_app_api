export function Card({ className = "", children, ...props }) {
  return (
    <div
      className={`bg-white rounded-lg shadow-md overflow-hidden ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ className = "", children }) {
  return <div className={`px-6 py-4 border-b ${className}`}>{children}</div>;
};

Card.Body = function CardBody({ className = "", children }) {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>;
};

Card.Footer = function CardFooter({ className = "", children }) {
  return (
    <div className={`px-6 py-4 border-t bg-gray-50 ${className}`}>
      {children}
    </div>
  );
};
