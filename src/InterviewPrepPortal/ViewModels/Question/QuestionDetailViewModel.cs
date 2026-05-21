using InterviewPrepPortal.Models;
using Q = InterviewPrepPortal.JsonModels.Question;
using Cat = InterviewPrepPortal.JsonModels.Category;

namespace InterviewPrepPortal.ViewModels.Question;

public class QuestionDetailViewModel
{
    public Q Question { get; set; } = null!;
    public Cat Category { get; set; } = null!;
    public UserProgress? Progress { get; set; }
    public UserCustomAnswer? CustomAnswer { get; set; }
    public UserNote? Note { get; set; }
    public List<Q> CrossReferences { get; set; } = [];
    public Q? PreviousQuestion { get; set; }
    public Q? NextQuestion { get; set; }
}
