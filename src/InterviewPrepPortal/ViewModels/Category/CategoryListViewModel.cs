using InterviewPrepPortal.Interfaces;
using InterviewPrepPortal.JsonModels;

namespace InterviewPrepPortal.ViewModels.Category;

public class CategoryListViewModel
{
    public List<CategoryWithStats> Categories { get; set; } = [];
}

public class CategoryWithStats
{
    public JsonModels.Category Category { get; set; } = null!;
    public int TotalQuestions { get; set; }
    public CategoryProgressSummary? Progress { get; set; }
}
