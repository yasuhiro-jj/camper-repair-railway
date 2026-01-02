type ContainerProps = {
  children: React.ReactNode;
  className?: string;
};

export default function Container({ children, className = "" }: ContainerProps) {
  return (
    <div className={`mx-auto w-full max-w-6xl px-4 py-12 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
}




