/** Shimmer skeleton placeholder while AI fetches products */
export default function SkeletonCard() {
  return (
    <div className="bg-s3 border border-border rounded-2xl overflow-hidden flex flex-col">
      {/* Image placeholder */}
      <div className="skeleton h-48 w-full" />

      {/* Info placeholder */}
      <div className="p-3 flex flex-col gap-2.5">
        <div className="skeleton h-3.5 w-4/5" />
        <div className="skeleton h-3 w-2/3" />
        <div className="skeleton h-5 w-1/3" />
        <div className="flex gap-1.5 mt-1">
          <div className="skeleton h-4 w-12" />
          <div className="skeleton h-4 w-14" />
          <div className="skeleton h-4 w-10" />
        </div>
        <div className="skeleton h-8 w-full mt-1 rounded-lg" />
      </div>
    </div>
  );
}
