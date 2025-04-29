
import { useQuery } from "@tanstack/react-query";
import { VideosResponse, Video } from "@/types/video";

// Mock data for demonstration purposes
export const MOCK_VIDEOS: Video[] = [
  {
    id: "1",
    title: "Passionate Couple Enjoying Intimate Moments",
    thumbnail: "https://placehold.co/640x360/1A1F2C/9b87f5?text=Video+1",
    url: "https://example.com/videos/1.mp4",
    duration: "12:34",
    viewCount: 1250000,
    uploadDate: "2 weeks ago",
    tags: ["passionate", "couple", "intimate"],
    category: "Couples",
    description: "A beautiful couple sharing their most intimate moments together in this exclusive high-definition video."
  },
  {
    id: "2",
    title: "Solo Performance with Toys",
    thumbnail: "https://placehold.co/640x360/1A1F2C/D946EF?text=Video+2",
    url: "https://example.com/videos/2.mp4",
    duration: "8:22",
    viewCount: 987500,
    uploadDate: "3 days ago",
    tags: ["solo", "toys", "orgasm"],
    category: "Solo"
  },
  {
    id: "3",
    title: "Hot Threesome Exploration",
    thumbnail: "https://placehold.co/640x360/1A1F2C/9b87f5?text=Video+3",
    url: "https://example.com/videos/3.mp4",
    duration: "15:47",
    viewCount: 1875000,
    uploadDate: "1 month ago",
    tags: ["threesome", "exploration", "passionate"],
    category: "Group"
  },
  {
    id: "4",
    title: "Sensual Massage Leads to More",
    thumbnail: "https://placehold.co/640x360/1A1F2C/D946EF?text=Video+4",
    url: "https://example.com/videos/4.mp4",
    duration: "21:09",
    viewCount: 567800,
    uploadDate: "1 week ago",
    tags: ["massage", "sensual", "orgasm"],
    category: "Massage"
  },
  {
    id: "5",
    title: "Amateur Couple's First On-Camera Experience",
    thumbnail: "https://placehold.co/640x360/1A1F2C/9b87f5?text=Video+5",
    url: "https://example.com/videos/5.mp4",
    duration: "19:23",
    viewCount: 782300,
    uploadDate: "5 days ago",
    tags: ["amateur", "couple", "first-time"],
    category: "Amateur"
  },
  {
    id: "6",
    title: "Intense BDSM Session",
    thumbnail: "https://placehold.co/640x360/1A1F2C/D946EF?text=Video+6",
    url: "https://example.com/videos/6.mp4",
    duration: "25:11",
    viewCount: 1345600,
    uploadDate: "2 months ago",
    tags: ["bdsm", "intense", "roleplay"],
    category: "BDSM"
  },
  {
    id: "7",
    title: "Romantic Evening Turns Passionate",
    thumbnail: "https://placehold.co/640x360/1A1F2C/9b87f5?text=Video+7",
    url: "https://example.com/videos/7.mp4",
    duration: "14:57",
    viewCount: 456700,
    uploadDate: "3 weeks ago",
    tags: ["romantic", "passionate", "couple"],
    category: "Romantic"
  },
  {
    id: "8",
    title: "Public Adventure in the Park",
    thumbnail: "https://placehold.co/640x360/1A1F2C/D946EF?text=Video+8",
    url: "https://example.com/videos/8.mp4",
    duration: "10:33",
    viewCount: 892400,
    uploadDate: "4 days ago",
    tags: ["public", "adventure", "outdoor"],
    category: "Public"
  },
  {
    id: "9",
    title: "Hot Office Romance After Hours",
    thumbnail: "https://placehold.co/640x360/1A1F2C/9b87f5?text=Video+9",
    url: "https://example.com/videos/9.mp4",
    duration: "17:45",
    viewCount: 567800,
    uploadDate: "1 week ago",
    tags: ["office", "romance", "roleplay"],
    category: "Office"
  },
  {
    id: "10",
    title: "Steamy Shower Session",
    thumbnail: "https://placehold.co/640x360/1A1F2C/D946EF?text=Video+10",
    url: "https://example.com/videos/10.mp4",
    duration: "11:28",
    viewCount: 723400,
    uploadDate: "6 days ago",
    tags: ["shower", "wet", "solo"],
    category: "Solo"
  },
  {
    id: "11",
    title: "Exciting Roleplay Fantasy",
    thumbnail: "https://placehold.co/640x360/1A1F2C/9b87f5?text=Video+11",
    url: "https://example.com/videos/11.mp4",
    duration: "22:17",
    viewCount: 1238900,
    uploadDate: "3 weeks ago",
    tags: ["roleplay", "fantasy", "costume"],
    category: "Roleplay"
  },
  {
    id: "12",
    title: "Intimate Yoga Session",
    thumbnail: "https://placehold.co/640x360/1A1F2C/D946EF?text=Video+12",
    url: "https://example.com/videos/12.mp4",
    duration: "16:42",
    viewCount: 435600,
    uploadDate: "2 weeks ago",
    tags: ["yoga", "flexible", "sensual"],
    category: "Fitness"
  }
];

const apiUrl = import.meta.env.VITE_API_BASE_URL;

const fetchVideos = async (page: number = 1, id?: string): Promise<VideosResponse> => {
  // Try to fetch from the API first
  try {
    let response;

    if (id) {
      // Fetch a specific video by ID
      response = await fetch(`${apiUrl}/api/videos/${id}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
    } else {
      // Fetch videos by page
      response = await fetch(`${apiUrl}/api/videos`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ page }),
      });
    }

    if (response.ok) {
      const data = await response.json();

      // If fetching by ID, wrap the single video in the `videos` array
      if (id) {
        return {
          videos: data.videos, // Wrap the single video in an array
          total: 1,
          page,
        };
      }

      // Return the paginated videos response
      return data;
    }

    // If API fails, return mock data
    console.log("Falling back to mock data");
    throw new Error("API fetch failed, using mock data");
  } catch (error) {
    console.log("Using mock videos data", error);

    // Calculate pagination for mock data
    const startIdx = (page - 1) * 12;
    const endIdx = startIdx + 12;
    const paginatedVideos = MOCK_VIDEOS.slice(startIdx, endIdx);

    // Simulate API response delay
    await new Promise((resolve) => setTimeout(resolve, 500));

    if (id) {
      // Return mock data for a specific video
      const mockVideo = MOCK_VIDEOS.find((video) => video.id === id);
      if (!mockVideo) {
        throw new Error(`Mock video with id ${id} not found`);
      }
      return {
        videos: [mockVideo], // Wrap the single mock video in an array
        total: 1,
        page,
      };
    }

    // Return mock data for paginated videos
    return {
      videos: paginatedVideos,
      total: MOCK_VIDEOS.length,
      page,
    };
  }
};

// export function useVideos(page: number = 1) {
//   return useQuery({
//     queryKey: ["videos", page],
//     queryFn: () => fetchVideos(page),
//     placeholderData: (previousData) => previousData,
//     staleTime: 5 * 60 * 1000, // 5 minutes
//   });
// }

const fetchTrendingVideos = async (): Promise<VideosResponse> => {
  // Try to fetch from the API first
  try {
    let response; {
      // Fetch videos by page
      response = await fetch(`${apiUrl}/api/trending/videos`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
    }

    if (response.ok) {
      const data = await response.json();
      return data;
    }

    // If API fails, return mock data
    console.log("Falling back to mock data");
    throw new Error("API fetch failed, using mock data");
  } catch (error) {
    console.log("Using mock videos data", error);

    // Calculate pagination for mock data
    const startIdx = (2 - 1) * 12;
    const endIdx = startIdx + 12;
    const paginatedVideos = MOCK_VIDEOS.slice(startIdx, endIdx);

    // Simulate API response delay
    await new Promise((resolve) => setTimeout(resolve, 500));
    const curr_page = 1;

    // Return mock data for paginated videos
    return {
      videos: paginatedVideos,
      total: MOCK_VIDEOS.length
    };
  }
};
// export function useTrendingVideos(page: number = 1, id?: string) {
//   return useQuery({
//     queryKey: id ? ["video", id] : ["videos", page], // Use "video" key for specific video, "videos" for paginated
//     queryFn:() => (id ? fetchTrendingVideos(undefined, id) : fetchTrendingVideos(page)), // Fetch trending videos
//     placeholderData: (previousData) => previousData,
//     staleTime: 5 * 60 * 1000, // 5 minutes
//     });
// }

export function useTrendingVideos() {
  return useQuery({
    queryKey: ["trendingVideos"],
    queryFn: fetchTrendingVideos,
    placeholderData: (previousData) => previousData,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
export function useVideos(page: number = 1, id?: string) {
  return useQuery({
    queryKey: id ? ["video", id] : ["videos", page], // Use "video" key for specific video, "videos" for paginated
    queryFn: () => (id ? fetchVideos(undefined, id) : fetchVideos(page)), // Fetch by id or page
    placeholderData: (previousData) => previousData,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
// This function would be used for SSR
export async function getVideos(page: number = 1): Promise<VideosResponse> {
  try {
    // In a real SSR environment, you'd use the full URL
    const response = await fetch(`${apiUrl}/api/videos`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ page }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch videos");
    }

    return response.json();
  } catch (error) {
    console.error("Error fetching videos for SSR:", error);
    
    // Return mock data for SSR fallback
    const startIdx = (page - 1) * 12;
    const endIdx = startIdx + 12;
    const paginatedVideos = MOCK_VIDEOS.slice(startIdx, endIdx);
    
    return { 
      videos: paginatedVideos, 
      total: MOCK_VIDEOS.length,
      page
    };
  }
}
