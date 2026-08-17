using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using TechScope.Models;


namespace TechScope.Data
{
    // Herdamos de IdentityDbContext para incluir tabelas de autenticação
    public class ApplicationDbContext : IdentityDbContext<ApplicationUser>
    {
        // Construtor recebe opções configuradas no Program.cs
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<Company> Companies => Set<Company>();

        public DbSet<Job> Jobs => Set<Job>();

        public DbSet<Technology> Technologies => Set<Technology>();

        public DbSet<JobTechnology> JobTechnologies => Set<JobTechnology>();

        protected override void OnModelCreating(ModelBuilder builder)
        {
            base.OnModelCreating(builder);

            builder.Entity<Company>()
                .ToTable("Companies", table => table.ExcludeFromMigrations());
            // Configura a chave primária de Company.
            builder.Entity<Company>()
                .HasKey(company => company.Id);

            builder.Entity<Job>()
                .ToTable("Jobs", table => table.ExcludeFromMigrations());
            // Configura a chave primária de Job.
            builder.Entity<Job>()
                .HasKey(job => job.Id);
            // Configura:
            // Company 1 ---- N Job
            builder.Entity<Job>()
                .HasOne(job => job.Company)
                .WithMany(company => company.Jobs)
                .HasForeignKey(job => job.CompanyId)
                .OnDelete(DeleteBehavior.Cascade);

            builder.Entity<Technology>()
                .ToTable("Technologies", table => table.ExcludeFromMigrations());
            // Configura a chave primária de Technology.
            builder.Entity<Technology>()
                .HasKey(technology => technology.Id);

            builder.Entity<JobTechnology>()
                .ToTable("JobTechnologies", table => table.ExcludeFromMigrations());
            // PRIMARY KEY (job_id, technology_id)
            builder.Entity<JobTechnology>()
                .HasKey(jobTechnology => new
                {
                    jobTechnology.JobId,
                    jobTechnology.TechnologyId
                });

            // Configura:
            // Job 1 ---- N JobTechnology
            builder.Entity<JobTechnology>() 
                .HasOne(jobTechnology => jobTechnology.Job)
                .WithMany(job => job.JobTechnologies)
                .HasForeignKey(jobTechnology => jobTechnology.JobId)
                .OnDelete(DeleteBehavior.Cascade);

            // Configura:
            // Technology 1 ---- N JobTechnology
            builder.Entity<JobTechnology>()
                .HasOne(jobTechnology => jobTechnology.Technology)
                .WithMany(technology => technology.JobTechnologies)
                .HasForeignKey(jobTechnology => jobTechnology.TechnologyId)
                .OnDelete(DeleteBehavior.Cascade);
        }

    }

}
